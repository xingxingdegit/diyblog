from flask import request, g, render_template, redirect, url_for
from api.dbpool import with_db, with_redis
from cryptography.fernet import Fernet
from flask_socketio import disconnect
from api.setting import get_setting
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

def admin_url_auth(**kwargs):
    try:
        admin_url = kwargs.get('admin_url') or g.admin_url
        auth_admin_url = get_setting('admin_url')
        if admin_url == auth_admin_url:
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

# api访问登录失效以后由前端决定是否跳转到登录页面
@with_redis
def check_login_state(r_type='api'):
    if r_type == 'api':
        return_data = False, 'auth_invalid'
    elif r_type == 'page':
        admin_url = get_setting('admin_url')
        return_data = redirect(url_for('admin_login_page', admin_url=admin_url))
    else:
        return_data = False, 'auth_invalid'

    cookie = request.cookies
    username = cookie.get('username')
    session = cookie.get('session')
    if not (username and session):
        return return_data
    user_state = g.redis.hgetall(username)
    if not user_state:
        return return_data
    timestamp_now = int(datetime.datetime.now().timestamp())
    try:
        if user_state['active'] == 'online':
            if (timestamp_now - int(user_state['lasttime'])) < int(user_state['timeout']):
                cookie_key = user_state['cookie_key']
                cipher = Fernet(cookie_key.encode('utf-8'))
                session_decode = cipher.decrypt(session.encode('utf-8')).decode('utf-8')
                session_username, sessionid = session_decode.split()
                if session_username == username:
                    if sessionid == user_state['session_id']:
                        g.redis.hset(username, 'lasttime', timestamp_now)
                        return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return return_data

# only init
@with_db('read')
def init_auth():
    try:
        tables = g.db.query('show tables;')
        if tables[0] and (tables[1] == 0):
            return True, ''
        init = get_setting('install_init')
        if init == 0:
            return True, ''
    except Exception:
        log.error(traceback.format_exc())
    disconnect()
    log.error('func:init_auto|repeat init')
    return False, ''


# only login
def client_ip_unsafe(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """ redis data:  client_ip_unsafe_<base64 IP>: {'count': <number>, 'lasttime': <last_login_time>}
        """
        client = request.remote_addr
        timestamp_now = int(datetime.datetime.now().timestamp())
        client_key = 'client_ip_unsafe_{}'.format(base64.b64encode(client.encode('utf-8')).decode('utf-8'))
        log.info('client_key:{}'.format(client_key))
        client_data = g.redis.hgetall(client_key)

        setting_data = get_setting(['login_fail_count', 'login_blacklist_timeout', 'login_fail_lasttime'])
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


from config import site_url
from hashlib import sha256
import hmac

def cors_hash(src_string, src_hash):
    time_key = int(datetime.datetime.now().timestamp()) // 100
    salt_key = '{}_{}'.format(site_url, time_key)
    new_hash = hmac.new(salt_key.encode('utf-8'), src_string.encode('utf-8'), sha256).hexdigest()
    if src_hash == new_hash:
        return True

    time_key = time_key - 1
    salt_key = '{}_{}'.format(site_url, time_key)
    new_hash = hmac.new(salt_key.encode('utf-8'), src_string.encode('utf-8'), sha256).hexdigest()
    if src_hash == new_hash:
        return True
    return False

# only api use
def cors_auth(check=None):
    if check is None:
        check = ['json', 'cookie']

    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'cookie' in check:
                cookies = request.cookies
                cookie_hash = cookies.get('hash')
                cookie_list = []
                for cookie in cookies:
                    if (cookie is None) or (cookie == 'hash'):
                        continue
                    cookie_list.append(str(cookies[cookie]))
                
                cookie_list.sort()
                cookie_str = '_'.join(cookie_list)
                cookie_hash_auth = cors_hash(cookie_str, cookie_hash)
                if not cookie_hash_auth:
                    log.info('func:cors_auth|cookie auth fail')
                    return False, ''
    
            if 'josn' in check:
                form_data = request.get_json()
                form_hash = form_data.pop('hash')
                form_list = []
                for form in form_data:
                    if form is None:
                        continue
                    form_list.append(str(form_data[form]))
                form_list.sort()
                form_str = '_'.join(form_list)
                form_hash_auth = cors_hash(form_str, form_hash)
                if not form_hash_auth:
                    log.info('func:cors_auth|form auth fail')
                    return False, ''
    
            return func(*args, **kwargs)
        return wrapper
    return inner




def auth_mode(mode, *r_type):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if mode == 'init':
                state = init_auth()
            elif mode == 'login':
                state = check_login_state(*r_type)
                try:
                    state[0]
                except TypeError:
                    return state
            else:
                state = False

            if state[0]:
                return func(*args, **kwargs)
            else:
                return state
        return inner
    return wrapper

