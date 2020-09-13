from flask import g
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from api.dbpool import select, with_db
import logging
import traceback

log = logging.getLogger(__name__)


@admin_url_auth_wrapper('api')
@auth_mode('login')
def check_classname(class_name):
    # 返回值， 第二部分为True 表示存在,  False表示不存在
    try:
        if class_name:
            state = select('class', fields=['classname'], where={'classname': class_name})
            if state:
                return True, True
            else:
                return True, False
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
def check_tagname(tag_name):
    # 返回值， 第二部分为True 表示存在,  False表示不存在
    try:
        if tag_name:
            state = select('tags', fields=['tagname'], where={'tagname': tag_name})
            if state:
                return True, True
            else:
                return True, False
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@with_db('read')
def get_class_list(data=None):
    try:
        if data:
            with_op = data.get('with', '').strip()
            if with_op == 'with_count':
                page_num = int(data['page_num'])
                class_num_per_page = int(data['class_num_per_page'])
                offset = (page_num - 1) * class_num_per_page

                sql = r'''select c.id, c.classname, c.status, c.sort, c.intro, g.count from `class` as c left join 
                         (select class, count(class) as count from `posts` group by class) as g on c.id = g.class'''
                sql += r' order by `id` desc limit {},{};'.format(offset, class_num_per_page)
                data = g.db.query(sql)
                if data[0]:
                    fields = ['id', 'classname', 'status', 'sort', 'intro', 'count']
                    data = [dict(zip(fields, onedata)) for onedata in g.db.cur.fetchall()]
                    total_num_sql = r'''select count(id) from `class` where `status` in (1, 2);'''
                    state = g.db.query(total_num_sql)
                    if state[0]:
                        total_class_num = g.db.cur.fetchone()[0]
                        return_data = {'list_data': data, 'total_class_num': total_class_num}
                        return True, return_data
                else:
                    return False, ''
        else:
            data = g.db.select('class', fields=['id', 'classname', 'status', 'sort', 'intro'], where={'status': [1, 2]})
            if data[0]:
                return True, data[1][1]
            else:
                return False, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@with_db('read')
def get_tags_list(data=None):
    try:
        fields = ['id', 'tagname', 'status', 'intro']
        if data:
            with_op = data.get('with', '').strip()
            if with_op == 'with_page':
                page_num = int(data['page_num'])
                tag_num_per_page = int(data['tag_num_per_page'])
                offset = (page_num - 1) * tag_num_per_page
                data = select('tags', fields=fields, where={'status': [1, 2]}, sort_field='id', limit=tag_num_per_page, offset=offset)
                total_num_sql = r'''select count(id) from `tags` where `status` in (1, 2);'''
                state = g.db.query(total_num_sql)
                if state[0]:
                    total_tag_num = g.db.cur.fetchone()[0]
                    return_data = {'list_data': data, 'total_tag_num': total_tag_num}
                    return True, return_data

        data = g.db.select('tags', fields=fields, where={'status': [1, 2]})
        if data[0]:
            return True, data[1][1]
        else:
            return False, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def add_class(data):
    try:
        class_id = int(data.get('class_id', 0))
        class_name = data['class_name'].strip()
        class_sort = int(data['class_sort'])
        class_status = int(data['class_status'])
        class_intro = data.get('class_intro').strip()

        # 有id表示更新， 没id表示添加
        if class_id:
            write_data = {'classname': class_name, 'sort': class_sort, 'status': class_status, 'intro': class_intro}
            state = g.db.update('class', write_data, where={'id': class_id})
            if state[0]:
                return True, ''
        else:
            write_data = {'classname': class_name, 'sort': class_sort, 'status': class_status, 'intro': class_intro}
            state = g.db.insert('class', write_data)
            if state[0]:
                return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def add_tag(data):
    try:
        tag_id = int(data.get('tag_id', 0))
        tag_name = data['tag_name'].strip()
        tag_status = int(data['tag_status'])
        tag_intro = data.get('tag_intro', '').strip()

        # 有id表示更新， 没id表示添加
        if tag_id:
            write_data = {'tagname': tag_name, 'status': tag_status, 'intro': tag_intro}
            state = g.db.update('tags', write_data, where={'id': tag_id})
            if state[0]:
                return True, ''
        else:
            write_data = {'tagname': tag_name, 'status': tag_status, 'intro': tag_intro}
            state = g.db.insert('tags', write_data)
            if state[0]:
                return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def del_class(data):
    try:
        class_id = data['class_id']
        class_name = data['class_name'].strip()
        if class_id == 1:
            return False, '咋还删呢， 一定要删就只能操作数据库了'

        where_data = {'id': class_id, 'classname': class_name}
        state = g.db.delete('class', where=where_data)
        if state[0]:
            return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def del_tag(data):
    try:
        tag_id = data['tag_id']
        tag_name = data['tag_name'].strip()

        where_data = {'id': tag_id, 'tagname': tag_name}
        state = g.db.delete('tags', where=where_data)
        if state[0]:
            return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''