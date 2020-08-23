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


def handle_post_info(data):
    ''' 添加标签， 处理时间戳为字符串格式，处理状态码为文字 '''
    ''' 为了不让前端在重新处理一遍, 就在这里处理了 '''
    tags_list = set()   # 为了添加标签
    classes_list = set()
    status_data = {1: '已发布', 2: '草稿', 3: '已删除'}
    strftime = r'%Y-%m-%d %H:%M'
    for note in data:
        if 'create_time' in note:
            create_timestamp = note['create_time']
            timestamp_obj = datetime.datetime.fromtimestamp(create_timestamp)
            note['create_time'] = timestamp_obj.strftime(strftime)
        if 'update_time' in note:
            update_timestamp = note['update_time']
            timestamp_obj = datetime.datetime.fromtimestamp(update_timestamp)
            note['update_time'] = timestamp_obj.strftime(strftime)
        if 'class' in note:
            classes_list.add(note['class'])
        if 'tags' in note:
            for tag_id in note['tags'].split(','):
                tags_list.add(tag_id)
        if 'status' in note:
            note['status_str'] = status_data[note['status']]

    if tags_list:
        tags_data = select('tags', fields=['id', 'tagname'], where={'id': list(tags_list)})
        tags_dict = {tag['id']: tag['tagname'] for tag in tags_data}

    if classes_list:
        classes_data = select('class', fields=['id', 'classname'], where={'id': list(classes_list)})
        classes_dict = {clas['id']: clas['classname'] for clas in classes_data}

    for note in data:
        tag_list = []
        for tag_id in note['tags'].split(','):
            tag_list.append(tags_dict.get(tag_id, ''))
        note['tags_str'] = ','.join(tag_list)
        note['classes_str'] = classes_dict[note['class']]

    return data


@admin_url_auth_wrapper('api')
@auth_mode('login')
def get_post_list(data):
    page_num = data['page_num']
    post_num_per_page = data['post_num_per_page']
    offset = (page_num - 1) * post_num_per_page
    data = select('posts', fields=['id', 'title', 'create_time', 'class', 'tags', 'status', 'visits'], 
                  where={'status': [1, 2, 3]},
                  limit=post_num_per_page, offset=offset)
    data = handle_post_info(data)
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





