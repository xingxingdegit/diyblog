from flask import request, g
from dbpool import with_db, with_redis
import traceback
import base64
import datetime
import logging

log = logging.getLogger(__name__)


@with_db('read')
def init_auth():
    try:
        tables = g.db.query('show tables;')
        if not tables:
            return True
        setting = g.db.select('setting', fields=['key', 'value'], where={'key': 'install_init'})
        if setting[0]:
            if setting[1][0]:
                init = int(setting[1][1][0]['value'])
                if init == 0:
                    return True
    except Exception:
        log.error(traceback.format_exc())
    return False


@with_redis
def client_ip_unsafe():
    """ redis data:  client_ip_unsafe_<base64 IP>: {'count': <number>, 'lasttime': <last_login_time>}
    """
    client = request.remote_addr
    client_data = g.redis.get('client_ip_unsafe_{}'.format(base64.b64encode(client.encode('utf-8'))))
    if not client_data:
        return True
    else:
        try:
            fail_count = int(client_data['count'])
            last_time = int(client_data['lasttime'])
            setting = g.db.select('setting', fields=['key', 'value'], where={'key': ['login_fail_count', 'login_blacklist_timeout']})
            setting_data = {one_data['key']: int(one_data['value']) for one_data in setting[1][1]}
            timestamp_now = int(datetime.datetime.now().timestamp())
            if fail_count < setting['login_fail_count']:
                return True
            if (timestamp_now - last_time) > setting_data['login_blacklist_timeout']:
                return True
        except Exception:
            log.error(traceback.format_exc())
    return False


