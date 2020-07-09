import logging
import random
from base.redis import RedisGetConnect
from base.dbpool import  DbGetConnect
import datetime
from config import login_prefix_key_timeout
from config import user_timeout
from hashlib import sha256
import traceback


log = logging.getLogger(__name__)

def login(username, password, key):
    sha256_password = sha256(password.encode('utf-8')).hexdigest()
    with DbGetConnect('read') as db:
        db_data = db.select('users', where={'username': username})
    try:
        if len(db_data) != 1:
            log.error('op:login|username:{}|info:Incorrect number of users'.format(username))
            return False, None
        if db_data[0]['password'] == sha256_password:
            redis = RedisGetConnect()
            timestamp = redis.get(key).strip()
            if timestamp:
                timestamp_now = int(datetime.datetime.now().timestamp())
                if (timestamp_now - int(timestamp)) < login_prefix_key_timeout:
                    session_id = [0] * 20
                    for i in range(20):
                        session_id[i] = random.choice('0123456789')
                    session_id = '{}{}'.format(''.join(session_id), timestamp_now)
                    session_data = {
                        'session_id': session_id,
                        'lasttime': timestamp_now,
                        'active': 'online',
                    }
                    redis.hmset(username, session_data)
                    redis.expire(username, user_timeout)
                    return True, session_id
                else:
                    log.info('op:login|login_prefix_key is timeout')
            else:
                log.info('op:login|login_prefix_key is timeout or not exist')
        else:
            log.info('op:login|password is error')
    except Exception:
        log.error(traceback.format_exc())

    return False, None


def get_key():
    key = [0] * 10
    for i in range(10):
        key[i] = random.randrange(97, 123)
    timestamp = int(datetime.datetime.now().timestamp())
    key = 'loginPrefix{}:{}'.format(timestamp, bytes(key).decode('utf-8'))
    try:
        redis = RedisGetConnect()
        redis.set(key, int(timestamp), ex=login_prefix_key_timeout)
        data = True, key
    except Exception:
        log.error(traceback.format_exc())
        data = False, None
    return data


