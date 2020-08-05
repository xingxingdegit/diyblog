from flask import request, g, render_template
from api.dbpool import with_db, with_redis
from cryptography.fernet import Fernet
from flask_socketio import disconnect
import traceback
import base64
import datetime
import logging
import functools

log = logging.getLogger(__name__)

# 因为admin_url变量只在view层传递，而admin_rul_auth认证在api层。
# 所以把admin_rul变量保存在g变量，供admin_url_auth来认证。
def backend_g_admin_url(func):
    @functools.wraps(func)
    def wrapper(*args, admin_url, **kwargs):
        g.admin_url = admin_url
        return func(*args, **kwargs)
    return wrapper

@with_db('read')
def admin_url_auth(**kwargs):
    try:
        admin_url = kwargs.get('admin_url') or g.admin_url
        setting = g.db.select('setting', fields=['value'], where={'key': 'admin_url'})
        if setting[0]:
            if setting[1][0]:
                if admin_url == setting[1][1][0]['value']:
                    return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, 'url not found'

def admin_url_auth_wrapper(r_type):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            # 这里传递kwargs，是为了page页(view层)认证不需要添加backend_g_admin_url装饰器。
            state = admin_url_auth(**kwargs)
            try:
                kwargs.pop('admin_url')
            except KeyError:
                pass
            if state[0]:
                resp_data = func(*args, **kwargs)
                return resp_data
            else:
                if r_type == 'page':
                    return render_template('404.html'), 404
                elif r_type == 'api':
                    return state
                else:
                    pass
        return inner
    return wrapper

# 登录失效以后由前端决定是否跳转
@with_redis
def check_login_state():
    cookie = request.cookies
    log.error('cookie: {}'.format(cookie))
    username = cookie.get('username')
    session = cookie.get('session')
    if not (username and session):
        return False, 'auth_invalid'
    user_state = g.redis.hgetall(username)
    if not user_state:
        return False, 'auth_invalid'
    timestamp_now = int(datetime.datetime.now().timestamp())
    try:
        if user_state['active'] == 'online':
            if (timestamp_now - int(user_state['lasttime'])) < int(user_state['timeout']):
                cookie_key = user_state['cookie_key']
                cipher = Fernet(cookie_key.encode('utf-8'))
                session_decode = cipher.decrypt(session.encode('utf-8')).decode('utf-8')
                session_username, sessionid = session_decode.split()
                log.info('sessionid: {}'.format(type(sessionid)))
                if session_username == username:
                    if sessionid == user_state['session_id']:
                        return True, ''

    except Exception:
        log.error(traceback.format_exc())
    return False, 'auth_invalid'

# only init
@with_db('read')
def init_auth():
    try:
        tables = g.db.query('show tables;')
        if tables[0] and (tables[1] == 0):
            return True, ''
        setting = g.db.select('setting', fields=['key', 'value'], where={'key': 'install_init'})
        if setting[0]:
            if setting[1][0]:
                init = int(setting[1][1][0]['value'])
                if init == 0:
                    return True, ''
    except Exception:
        log.error(traceback.format_exc())
    disconnect()
    log.error('func:init_auto|repeat init')
    return False, ''


# only login
def client_ip_unsafe(func):
    @with_db('read')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """ redis data:  client_ip_unsafe_<base64 IP>: {'count': <number>, 'lasttime': <last_login_time>}
        """
        client = request.remote_addr
        timestamp_now = int(datetime.datetime.now().timestamp())
        client_key = 'client_ip_unsafe_{}'.format(base64.b64encode(client.encode('utf-8')).decode('utf-8'))
        log.info('client_key:{}'.format(client_key))
        client_data = g.redis.hgetall(client_key)

        setting = g.db.select('setting', fields=['key', 'value'], where={'key': ['login_fail_count', 'login_blacklist_timeout', 'login_fail_lasttime']})
        setting_data = {one_data['key']: int(one_data['value']) for one_data in setting[1][1]}
        auth = False

        if not client_data:
            auth = True
        else:
            try:
                fail_count = int(client_data['count'])
                last_time = int(client_data['lasttime'])
                if fail_count < setting_data['login_fail_count']:
                    auth = True
                if (timestamp_now - last_time) > setting_data['login_blacklist_timeout']:
                    auth = True
            except Exception:
                log.error(traceback.format_exc())
        if auth:
            resp_data = func(*args, **kwargs)
            if (resp_data[0] is False) and (resp_data[1] is False):
                if client_data:
                    fail_count = int(client_data['count'])
                    last_time = int(client_data['lasttime'])
                    if (timestamp_now - last_time) > setting_data['login_fail_lasttime']:
                        unsafe_data = {'count': 1, 'lasttime': timestamp_now}
                        g.redis.hmset(client_key, unsafe_data)
                    else:
                        unsafe_data = {'count': fail_count + 1, 'lasttime': timestamp_now}
                        g.redis.hmset(client_key, unsafe_data)
                else:
                    unsafe_data = {'count': 1, 'lasttime': timestamp_now}
                    g.redis.hmset(client_key, unsafe_data)
            elif resp_data[0] is True:
                g.redis.delete(client_key)

            return resp_data
        else:
            return False, '哈喽，进黑名单了'
    return wrapper



def auth_mode(mode):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if mode == 'init':
                state = init_auth()
            elif mode == 'login':
                state = check_login_state()
            else:
                state = False

            if state[0]:
                return func(*args, **kwargs)
            else:
                return state
        return inner
    return wrapper

