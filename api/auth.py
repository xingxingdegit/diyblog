from flask import request, g, render_template
from api.dbpool import with_db, with_redis
import traceback
import base64
import datetime
import logging
import functools

log = logging.getLogger(__name__)

@with_db('read')
def admin_url_auth(admin_url):
    try:
        setting = g.db.select('setting', fields=['value'], where={'key': 'admin_url'})
        if setting[0]:
            if setting[1][0]:
                if admin_url == setting[1][1][0]['value']:
                    return True
    except Exception:
        log.error(traceback.format_exc())
    return False

def admin_url_auth_wrapper(func):
    @functools.wraps(func)
    def wrapper(admin_url, *args, **kwargs):
        if admin_url_auth(admin_url):
            resp_data = func(*args, **kwargs)
            return resp_data
        else:
            return render_template('404.html'), 404
    return wrapper

@with_db('read')
def init_auth():
    from flask_socketio import disconnect
    try:
        tables = g.db.query('show tables;')
        if tables[0] and (tables[1] == 0):
            return True
        setting = g.db.select('setting', fields=['key', 'value'], where={'key': 'install_init'})
        if setting[0]:
            if setting[1][0]:
                init = int(setting[1][1][0]['value'])
                if init == 0:
                    return True
    except Exception:
        log.error(traceback.format_exc())
    disconnect()
    log.error('func:init_auto|repeat init')
    return False


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
                if init_auth():
                    return func(*args, **kwargs)
            else:
                pass
        return inner
    return wrapper

