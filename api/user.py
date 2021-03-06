import logging
import random
from cryptography.fernet import Fernet
from flask import g, request
from api.dbpool import  with_db, with_redis
from api.auth import client_ip_unsafe
import datetime
from hashlib import sha256
import traceback
from api.auth import admin_url_auth, admin_url_auth_wrapper, auth_mode, cors_auth
from api.setting import get_setting
from base64 import b64encode


log = logging.getLogger(__name__)

@admin_url_auth_wrapper('api')
@client_ip_unsafe
@with_db('read')
def login(username, password, key):
    sha256_password = sha256(password.encode('utf-8')).hexdigest()
    db_data = g.db.select('users', where={'username': username})
    try:
        if not db_data[0]:
            log.info('func:login|error happen in during database query')
            return False, None
        if db_data[1][0] > 1:
            log.error('func:login|username:{}|info:Incorrect number of users'.format(username))
            return False, None
        db_data = db_data[1][1]
        if db_data:
            if db_data[0]['password'] == sha256_password:
                timestamp = g.redis.get(key)
                if timestamp:
                    g.redis.delete(key)
                    timestamp_now = int(datetime.datetime.now().timestamp())
                    setting = get_setting(['login_prefix_key_timeout', 'user_timeout'])
                    if setting: 
                        if ('login_prefix_key_timeout' not in setting) or ('user_timeout' not in setting):
                            log.error('func:login|setting:{}|info:setting about user login have a question'.format(setting))
                            return False, None
                        if (timestamp_now - int(timestamp)) < setting['login_prefix_key_timeout']:
                            session_id = [0] * 30
                            for i in range(30):
                                session_id[i] = random.choice('0123456789')
                            session_id = '{}{}'.format(''.join(session_id), timestamp_now)
                            cookie_key = db_data[0]['cookie_key']
                            session_data = {
                                'session_id': session_id,
                                'lasttime': timestamp_now,
                                'active': 'online',
                                'cookie_key': cookie_key,
                                'timeout': setting['user_timeout'],
                            }
                            hash_username = b64encode(sha256(username.encode('utf-8')).digest()).decode('utf-8')
                            g.redis.hmset(hash_username, session_data)
                            g.redis.expire(hash_username, setting['user_timeout'])
                            cipher = Fernet(cookie_key.encode('utf-8'))
                            session = cipher.encrypt(('{} {}'.format(username, session_id)).encode('utf-8'))
                            return True, session
                        else:
                            log.info('func:login|user:{}|login_prefix_key is timeout'.format(username))
                    else:
                        log.info('func:login|error happen in during database query')
                else:
                    log.info('func:login|user:{}|login_prefix_key is timeout or not exist'.format(username))
            else:
                log.info('func:login|user:{}|password is error'.format(username))
                return False, False
        else:
            log.info('func:login|user:{}|not found user'.format(username))
            return False, False
    except Exception:
        log.error(traceback.format_exc())
    return False, None



@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_redis
def logout(username):
    try:
        hash_username = b64encode(sha256(username.encode('utf-8')).digest()).decode('utf-8')
        state = g.redis.delete(hash_username)
        if state:
            return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@client_ip_unsafe
def get_key():
    key = [0] * 10
    for i in range(10):
        key[i] = random.randrange(97, 123)
    timestamp = int(datetime.datetime.now().timestamp())
    key = 'loginPrefix{}:{}'.format(timestamp, bytes(key).decode('utf-8'))
    data = False, None
    try:
        setting = get_setting('login_prefix_key_timeout')
        if setting:
            login_prefix_key_timeout = setting
            g.redis.set(key, int(timestamp), ex=login_prefix_key_timeout)
            data = True, key
    except Exception:
        log.error(traceback.format_exc())
    return data


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def change_passwd(data, username):
    try:
        first = data['first']
        second = data['second']
        if first and second:
            if first == second:
                sha256_password = sha256(second.encode('utf-8')).hexdigest()
                state = g.db.update('users', {'password': sha256_password}, where={'username': username})
                if state[0]:
                    return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''
