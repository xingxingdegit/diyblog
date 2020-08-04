import logging
import random
from cryptography.fernet import Fernet
from flask import g
from api.dbpool import  with_db, with_redis
from api.auth import client_ip_unsafe
import datetime
from hashlib import sha256
import traceback


log = logging.getLogger(__name__)

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
                    setting = g.db.select(
                        'setting', fields=['key', 'value'], where={'key': ['login_prefix_key_timeout', 'user_timeout']})
                    if setting[0]: 
                        setting = {one_set['key']: int(one_set['value']) for one_set in setting[1][1]}
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
                            g.redis.hmset(username, session_data)
                            g.redis.expire(username, setting['user_timeout'])
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


@with_db('read')
def get_key():
    key = [0] * 10
    for i in range(10):
        key[i] = random.randrange(97, 123)
    timestamp = int(datetime.datetime.now().timestamp())
    key = 'loginPrefix{}:{}'.format(timestamp, bytes(key).decode('utf-8'))
    data = False, None
    try:
        setting = g.db.select('setting', fields=['key', 'value'], where={'key': 'login_prefix_key_timeout'})
        if setting[0]:
            login_prefix_key_timeout = setting[1][1][0]['value']
            g.redis.set(key, int(timestamp), ex=login_prefix_key_timeout)
            data = True, key
    except Exception:
        log.error(traceback.format_exc())
    return data



