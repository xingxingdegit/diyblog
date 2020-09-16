from api.dbpool import with_db, select, with_redis
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from flask import g
import logging
import traceback
import datetime

log = logging.getLogger(__name__)



@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth('cookie')
@with_db('read')
def get_static_notice():
    try:
        notice = select('notice', fields=['content', 'status'], where={'id': 1, 'type': 1})
        if notice:
            return True, notice[0]
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


# 前台使用
def get_static_notice_fw():
    try:
        notice = select('notice', fields=['content'], where={'id': 1, 'type': 1, 'status': 1})
        if notice[0]:
            return True, notice
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def set_static_notice(data):
    try:
        notice_info = data['notice_info'].strip()
        status = int(data['status'])
        timestamp = int(datetime.datetime.now().timestamp())
        if notice_info:
            use_data = {'content': notice_info, 'status': status, 'uptime': timestamp}
            state = g.db.update('notice', use_data, where={'id': 1, 'type': 1})
            if state[0]:
                return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''