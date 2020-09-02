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
        if return_data:
            return True, return_data
    except Exception:
        log.error(traceback.format_exc())
    return False, ''

@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def remove_post(data):
    '''标记为已删除'''
    try:
        post_id = int(data.get('post_id', 0))
        if post_id:
            state = g.db.update('posts', values={'status': 3}, where={'id': post_id})
            if state[0]:
                return True, state[1]
    except Exception:
        log.error(traceback.format_exc())
    return False, ''

@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def cancel_remove(data):
    '''取消删除标记，文档变为草稿状态'''
    try:
        post_id = int(data.get('post_id', 0))
        if post_id:
            state = g.db.update('posts', values={'status': 2}, where={'id': post_id})
            if state[0]:
                return True, state[1]
    except Exception:
        log.error(traceback.format_exc())
    return False, ''

@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('delete')
def del_post(data):
    '''彻底删除文档'''
    try:
        post_id = int(data.get('post_id', 0))
        if post_id:
            state = g.db.delete('posts', where={'id': post_id})
            if state[0]:
                return True, state[1]

    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
def get_post_admin(data):
    try:
        id = data['id']
        filter = data.get('filter')
        if id and filter == 'state_publish':
            data = select('posts', fields=['id', 'title', 'create_time', 'summary', 'class', 'tags', 'url'], where={'id': id})
        elif id:
            data = select('posts', fields=['id', 'title', 'create_time', 'summary', 'posts', 'code_style','class', 'tags', 'url'], where={'id': id})
        if len(data) > 1:
            log.error('func:get_post_admin|post_id:{}|post number > 1'.format(id))
            return False, ''
        else:
            data = data[0]
            data['tags'] = list(map(int, data['tags'].split(',')))
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
            tag_list.append(tags_dict.get(int(tag_id), ''))
        note['tags_str'] = ','.join(tag_list)
        note['classes_str'] = classes_dict[note['class']]

    return data


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('read')
def get_post_list(data):
    try:
        page_num = int(data['page_num'])
        post_num_per_page = int(data['post_num_per_page'])
        offset = (page_num - 1) * post_num_per_page
        search_on = data.get('search_on', False)

        fields=['id', 'title', 'create_time', 'class', 'tags', 'status', 'visits']
        if search_on is True:
            new_fields = list(map(lambda x: '`{}`'.format(x), fields))
            sql = r'''select {} from `posts` where '''.format(','.join(new_fields))
            keyword = data.get('search_keyword', '').strip()
            post_class = int(data.get('search_class', 0))
            status = int(data.get('search_status', 0))
            search_where = []
            if keyword:
                search_where.append('`posts` like "%{}%"'.format(g.db.conn.escape_string(keyword)))
            if post_class:
                search_where.append('`class` = "{}"'.format(post_class))
            if status:
                search_where.append('`status` = "{}"'.format(status))
            else:
                search_where.append('`status` in (1,2)')
            sql_where = r' and '.join(search_where)
            sql += sql_where
            sql += r' order by `update_time` desc limit {},{};'.format(offset, post_num_per_page)
            state = g.db.query(sql)
            if state[0]:
                data = [dict(zip(fields, onedata)) for onedata in g.db.cur.fetchall()]
            else:
                return False, ''
        else:
            sql_where = '`status` in (1,2)'
            data = select('posts', fields=fields, where={'status': [1, 2]}, sort_field='update_time', limit=post_num_per_page, offset=offset)

        data = handle_post_info(data)
        total_num_sql = r'''select count(id) from `posts` where {}'''.format(sql_where)
        # 查询复合条件的有多少条， 作为前端'总条数'的展示数据
        state = g.db.query(total_num_sql)
        if state[0]:
            total_post_num = g.db.cur.fetchone()[0]
        else:
            total_post_num = 0

        return_data = {'list_data': data, 'total_post_num': total_post_num}

        return True, return_data
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


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
@cors_auth()
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


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def publish_post(data):
    ''' 通过id判断是更新还是创建。  在第一次保存草稿以后，会返回id值，便于第二次保存变为更新 '''
    try:
        title = data['post_title'].strip()
        content = data['post_content']
        code_style = data['code_style'].strip()
        class_id = int(data.get('post_class', 1))
        tags_id = data.get('post_tags', '')
        url = data['post_url'].strip()
        create_time = int(data['post_create_datetime'])
        update_time = int(data['post_update_datetime'])
        summary = data.get('post_summary', '').strip()
        post_id = int(data.get('post_id', 0))

        if len(str(create_time)) > 10:
            create_time = int(str(create_time)[0:10])
        if len(str(update_time)) > 10:
            update_time = int(str(update_time)[0:10])

        if isinstance(tags_id, list):
            tags_id = ','.join(map(str, tags_id))

        write_data = {
            'title': title, 
            'posts': content, 
            'status': 1, 
            'code_style': code_style,
            'class': class_id,
            'tags': tags_id,
            'url': url,
            'create_time': create_time,
            'update_time': update_time,
            'summary': summary,
        }
        if post_id:
            state = g.db.update('posts', write_data, where={'id': post_id})
            # 如果没有更新成功，前端提示注意保存本地
            if state[0] and state[1]:
                return True, ''
            elif state[0] and state[1] == 0:
                return False, 'not_change'
        else:
            timestamp_now = int(datetime.datetime.now().timestamp())
            write_data['id'] = timestamp_now
            state = g.db.insert('posts', write_data)
            if state[0] and state[1]:
                post_id = select('posts', fields=['id'], where={'title': title})[0]['id']
                if post_id:
                    return True, {'id': post_id}
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def publish_post_state(data):
    try:
        class_id = int(data.get('post_class', 1))
        tags_id = data.get('post_tags', '')
        url = data['post_url'].strip()
        create_time = int(data['post_create_datetime'])
        update_time = int(data['post_update_datetime'])
        summary = data.get('post_summary', '').strip()
        post_id = int(data['post_id'])

        if len(str(create_time)) > 10:
            create_time = int(str(create_time)[0:10])
        if len(str(update_time)) > 10:
            update_time = int(str(update_time)[0:10])

        if isinstance(tags_id, list):
            tags_id = ','.join(map(str, tags_id))

        write_data = {
            'status': 1, 
            'class': class_id,
            'tags': tags_id,
            'url': url,
            'create_time': create_time,
            'update_time': update_time,
            'summary': summary,
        }
        if post_id:
            state = g.db.update('posts', write_data, where={'id': post_id})
            # 如果没有更新成功，前端提示注意保存本地
            if state[0] and state[1]:
                return True, ''
            elif state[0] and state[1] == 0:
                return False, 'not_change'
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def publish_cancel(data):
    try:
        post_id = int(data['post_id'])
        write_data = {'status': 2}
        if post_id:
            state = g.db.update('posts', write_data, where={'id': post_id})
            # 如果没有更新成功，前端提示注意保存本地
            if state[0] and state[1]:
                return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''

