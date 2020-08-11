from api.dbpool import with_db, select
from api.auth import admin_url_auth_wrapper, auth_mode
from flask import g
import logging
import traceback
import datetime

log = logging.getLogger(__name__)

@admin_url_auth_wrapper('api')
@auth_mode('login')
@with_db('read')
def check_title(title):
    try:
        data = g.db.select('posts', fields=['title'], where={'title': title})
        if data[0]:
            if data[1][0] == 0:
                return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@with_db('read')
def check_url(url):
    try:
        data = g.db.select('posts', fields=['urls'], where={'title': url})
        if data[0]:
            if data[1][0] == 0:
                return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''

@admin_url_auth_wrapper('api')
@auth_mode('login')
@with_db('write')
def save_post(data):
    ''' 通过id判断是更新还是创建。  在第一次保存草稿以后，会返回id值，便于第二次保存变为更新 '''
    try:
        title = data['title']
        content = data['content']
        id = data['id']

        timestamp_now = int(datetime.datetime.now().timestamp())
        write_data = {'title': title, 'posts': content, 'status': 2}
        if id:
            write_data['update_time'] = timestamp_now
            state = g.db.update('posts', write_data, where={'id': id})
            # 如果没有更新成功，前端提示注意保存本地
            if state[0] and state[1]:
                return True, ''
        else:
            write_data['create_time'] = timestamp_now
            write_data['update_time'] = timestamp_now
            write_data['id'] = timestamp_now
            state = g.db.insert('posts', write_data)
            if state[0] and state[1]:
                id = select('posts', fields=['id'], where={'title': title})[0]['id']
                if id:
                    return True, id
    except Exception:
        log.error(traceback.format_exc())
    return False, ''





