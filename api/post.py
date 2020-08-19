from api.dbpool import with_db, select, with_redis
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from flask import g
import logging
import traceback
import datetime

log = logging.getLogger(__name__)

@admin_url_auth_wrapper('api')
@auth_mode('login')
def check_something(data):
    # check title 与 url是否存在, 已存在返回True,  返回一个字典，{title: True, url: True}
    try:
        title = data['title']
        url = data['url']
        return_data = {}
        if title:
            title = select('posts', fields=['title'], where={'title': title})
            if title:
                return_data['title'] = True
            else:
                return_data['title'] = False
        if url:
            url = select('posts', fields=['url'], where={'url': url})
            if url:
                return_data['url'] = True
            else:
                return_data['url'] = False
        return True, return_data
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth
def get_post_admin(data):
    try:
        id = data['id']
        if id:
            data = select('posts', fields=['id', 'title', 'create_time', 'summary', 'posts', 'code_style','class', 'url'], where={'id': id})
            if len(data) > 1:
                log.error('func:get_post_admin|post_id:{}|post number > 1'.format(id))
                return False, ''
            else:
                data = data[0]
                return True, data
    except Exception:
        log.error(traceback.format_exc())
    return False, ''

@admin_url_auth_wrapper('api')
@auth_mode('login')
def get_post_list(data):
    page_num = data['page_num']
    post_num_per_page = data['post_num_per_page']
    offset = (page_num - 1) * post_num_per_page
    data = select('posts', fields=['id', 'title', 'create_time', 'class', 'status', 'visits'], limit=post_num_per_page, offset=offset)
    return True, data


# 首页的访问， 不需要权限
def get_post_index(data):
    try:
        url = data['url']
        if url:
            data = select('posts', fields=['title', 'create_time', 'update_time', 'posts', 'code_style','visits'],where={'url': url})
            data = data[0]
        else:
            data = select('posts', fields=['title', 'create_time', 'update_time', 'summary', 'class', 'visits'])
            # 需要分页处理， 添加where条件。
            pass
        return True, data
    except Exception:
        log.error(traceback.format_exc())
        return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth
@with_db('write')
def save_post(data):
    ''' 通过id判断是更新还是创建。  在第一次保存草稿以后，会返回id值，便于第二次保存变为更新 '''
    try:
        title = data['title']
        content = data['content']
        code_style = data['code_style']
        id = data['id']

        timestamp_now = int(datetime.datetime.now().timestamp())
        write_data = {'title': title, 'posts': content, 'status': 2, 'code_style': code_style}
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
                    return True, {'id': id}
    except Exception:
        log.error(traceback.format_exc())
    return False, ''





