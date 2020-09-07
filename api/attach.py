from api.dbpool import with_db, select, with_redis
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from flask import g, url_for
import logging
import traceback
import datetime
import os
from PIL import Image, UnidentifiedImageError
from config import basedir
from config import private_data_dir
from config import site_url
from api.setting import get_setting

log = logging.getLogger(__name__)


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def invalid_attach(data):
    '''失效附件'''
    try:
        filename = data.get('file_name', '').strip()
        file_id = int(data.get('file_id', 0))
        only_filename, ext_name = filename.split('.')
        file_info = select('attach', fields=['pathname', 'private', 'status'], where={'filename': filename, 'id': file_id})[0]
        if file_info:
            pathname = file_info['pathname']
            private = file_info['private']
            status = file_info['status']
            if status == 2:
                return False, 'file already invalid'

            invalid_filename = '{}_{}.{}'.format(only_filename, 'invalid', ext_name)
            invalid_file_pathname = os.path.dirname(pathname) + '/{}'.format(invalid_filename)
            if private == 1:
                src_file_pathname = basedir / pathname
                dest_file_pathname = basedir / invalid_file_pathname
            elif private == 2:
                src_file_pathname = basedir / private_data_dir / pathname
                dest_file_pathname = basedir / private_data_dir / invalid_file_pathname
            else:
                log.error('fund:invalid_attach|private:{}|private is error'.format(private))
                return False, ''
            try:
                g.db.begin()
                state = g.db.update('attach', {'status': 2}, where={'filename': filename, 'id': file_id})
                if state[0] and state[1] == 1:
                    os.rename(src_file_pathname, dest_file_pathname)
                    g.db.commit()
                    return True, ''
                else:
                    g.db.rollback()
                    log.error('fund:invalid_attach|state:{}|db exec state is error'.format(state))
            except Exception:
                log.error(traceback.format_exc())
                g.db.rollback()

    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def recover_attach(data):
    '''恢复附件'''
    try:
        filename = data.get('file_name', '').strip()
        file_id = int(data.get('file_id', 0))
        only_filename, ext_name = filename.split('.')
        file_info = select('attach', fields=['pathname', 'private', 'status'], where={'filename': filename, 'id': file_id})[0]
        if file_info:
            pathname = file_info['pathname']
            private = file_info['private']
            status = file_info['status']
            if status == 1:
                return False, 'file already recover'

            invalid_filename = '{}_{}.{}'.format(only_filename, 'invalid', ext_name)
            invalid_file_pathname = os.path.dirname(pathname) + '/{}'.format(invalid_filename)
            if private == 1:
                src_file_pathname = basedir / invalid_file_pathname
                dest_file_pathname = basedir / pathname
            elif private == 2:
                src_file_pathname = basedir / private_data_dir / invalid_file_pathname
                dest_file_pathname = basedir / private_data_dir / pathname
            else:
                log.error('fund:recover_attach|private:{}|private is error'.format(private))
                return False, ''
            try:
                g.db.begin()
                state = g.db.update('attach', {'status': 1}, where={'filename': filename, 'id': file_id})
                if state[0] and state[1] == 1:
                    os.rename(src_file_pathname, dest_file_pathname)
                    g.db.commit()
                    return True, ''
                else:
                    g.db.rollback()
                    log.error('fund:recover_attach|state:{}|db exec state is error'.format(state))
            except Exception:
                log.error(traceback.format_exc())
                g.db.rollback()
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def delete_attach(data):
    '''删除附件'''
    try:
        filename = data.get('file_name', '').strip()
        file_id = int(data.get('file_id', 0))
        file_info = select('attach', fields=['pathname', 'private', 'status'], where={'filename': filename, 'id': file_id})[0]
        if file_info:
            pathname = file_info['pathname']
            private = file_info['private']
            status = file_info['status']
            if status == 1:
                dest_file_pathname = pathname
            elif status == 2:
                only_filename, ext_name = filename.split('.')
                dest_filename = '{}_{}.{}'.format(only_filename, 'invalid', ext_name)
                dest_file_pathname = os.path.dirname(pathname) + '/{}'.format(dest_filename)
            else:
                log.error('fund:delete_attach|status:{}|status is error'.format(status))
                return False, ''

            if private == 1:
                sys_file_pathname = basedir / dest_file_pathname
            elif private == 2:
                sys_file_pathname = basedir / private_data_dir / dest_file_pathname
            else:
                log.error('fund:delete_attach|private:{}|private is error'.format(private))
                return False, ''
            try:
                g.db.begin()
                state = g.db.delete('attach', where={'filename': filename, 'id': file_id})
                if state[0] and state[1] == 1:
                    os.remove(sys_file_pathname)
                    g.db.commit()
                    delete_mini_photo(pathname, private)
                    return True, ''
                else:
                    g.db.rollback()
                    log.error('fund:delete_attach|state:{}|db exec state is error'.format(state))
            except Exception:
                log.error(traceback.format_exc())
                g.db.rollback()
    except Exception:
        log.error(traceback.format_exc())
    return False, ''

def delete_mini_photo(pathname, private):
    dir_pathname, filename = os.path.split(pathname)
    if private == 1:
        sys_dest_dirpath = basedir / dir_pathname
    elif private == 2:
        sys_dest_dirpath = basedir / private_data_dir / dir_pathname
    else:
        log.error('fund:delete_mini_photo|private:{}|private is error'.format(private))
        return False

    only_filename, ext_name = filename.split('.')
    for size in ('64', '128', '256', '512'):
        dest_filename = '{}_{}.{}'.format(only_filename, size, ext_name)
        sys_file_pathname = sys_dest_dirpath / dest_filename
        if sys_file_pathname.exists():
            try:
                os.remove(sys_file_pathname)
            except Exception:
                pass
    else:
        return True


@auth_mode('login')
def get_private_file(private_file):
    try:
        mimetype_first, only_filename_with_ext = private_file.split('-')
        only_filename, ext_name = only_filename_with_ext.split('.')

        setting = get_setting(['upload_file_ext', 'upload_file_mime'])
        if ext_name not in setting['upload_file_ext'].split(','):
            log.error('fund:get_private_file|ext_name:{}|ext_name not in setting'.format(ext_name))
            return False, ''
        if mimetype_first not in setting['upload_file_mime'].split(','):
            log.error('fund:get_private_file|file_mime:{}|master mime not in setting'.format(mimetype_first))
            return False, ''

        time_str = ''
        for i in range(0, 19, 2):
            time_str += only_filename[i]
        file_datetime = datetime.datetime.fromtimestamp(int(time_str))
        file_year = '{}'.format(file_datetime.year)
        file_month = '{:02}'.format(file_datetime.month)
        filename = '{}-{}.{}'.format(mimetype_first, only_filename, ext_name)
        system_filepath = basedir / private_data_dir / file_year / file_month / filename
        if os.access(system_filepath, os.R_OK):
            return True, system_filepath
        else:
            log.error('fund:get_private_file|system_filepath:{}|file not exist or cant not read'.format(mimetype_first))
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('read')
def get_mini_photo(data):
    filename = data['filename']
    size_level = data['size_level']
    return make_mini_photo(filename, size_level)


def make_mini_photo(filename, size_level):
    try:
        level = {1: (64, 64), 2: (128, 128), 3: (256, 256), 4: (512, 512)}
        file_info = select('attach', fields=['pathname', 'mimetype', 'private', 'is_image'], where={'filename': filename})[0]
        if file_info:
            pathname = file_info['pathname']
            is_image = file_info['is_image']
            private = file_info['private']

            only_filename, ext_name = filename.split('.')

            if is_image == 1:
                mini_filename = '{}_{}.{}'.format(only_filename, level[size_level][0], ext_name)
                mini_file_pathname = os.path.dirname(pathname) + '/{}'.format(mini_filename)

                if private == 1:
                    url_path = '{}/{}'.format(site_url, mini_file_pathname)
                    src_file_pathname = basedir / pathname
                    dest_file_pathname = basedir / mini_file_pathname
                elif private == 2:
                    url_path = '{}{}'.format(site_url, url_for('get_private_file_view', private_file=mini_filename))
                    src_file_pathname = basedir / private_data_dir / pathname
                    dest_file_pathname = basedir / private_data_dir / mini_file_pathname
                else:
                    return False, ''

                if dest_file_pathname.exists():
                    return True, url_path
                else:
                    im = Image.open(src_file_pathname)
                    im.thumbnail(level[size_level])
                    im.save(dest_file_pathname)
                    return True, url_path
            else:
                return False, 'format_not_support'
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth('cookie')
@with_db('read')
def get_mimetype_list():
    try:
        sql = r'''select mimetype from `attach` group by "mimetype"'''
        state = g.db.query(sql)
        if state[0]:
            data = [mimetype[0] for mimetype in g.db.cur.fetchall()]
            return True, data
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('read')
def get_attach_list(data):
    try:
        page_num = int(data['page_num'])
        attach_num_per_page = int(data['attach_num_per_page'])
        offset = (page_num - 1) * attach_num_per_page
        search_on = data.get('search_on', False)
        size_level = int(data.get('size_level', 0))

        fields=['id', 'filename', 'is_image', 'pathname', 'mimetype', 'size', 'width', 'height', 'uptime', 'status', 'private', 'intro']
        if search_on is True:
            new_fields = list(map(lambda x: '`{}`'.format(x), fields))
            sql = r'''select {} from `attach` where '''.format(','.join(new_fields))
#            size = int(data.get('size', 0))  # size: 100,   100-200
#            width = int(data.get('width', 0))
#            height = int(data.get('height', 0))
            mimetype = data.get('search_mimetype', '').strip()
            private = int(data.get('search_private', 0))
            status = int(data.get('search_status', 1))
            search_where = []
            if mimetype:
                search_where.append('`mimetype` = "{}"'.format(g.db.conn.escape_string(mimetype)))
            if private:
                search_where.append('`private` = "{}"'.format(private))
            if status:
                search_where.append('`status` = "{}"'.format(status))
            else:
                search_where.append('`status` = "1"')
            sql_where = r' and '.join(search_where)
            sql += sql_where
            sql += r' order by `uptime` desc limit {},{};'.format(offset, attach_num_per_page)
            state = g.db.query(sql)
            if state[0]:
                data = [dict(zip(fields, onedata)) for onedata in g.db.cur.fetchall()]
            else:
                return False, ''
        else:
            sql_where = '`status` = 1'
            data = select('attach', fields=fields, where={'status': 1}, sort_field='uptime', limit=attach_num_per_page, offset=offset)

        total_num_sql = r'''select count(id) from `attach` where {}'''.format(sql_where)
        # 查询复合条件的有多少条， 作为前端'总条数'的展示数据
        state = g.db.query(total_num_sql)
        if state[0]:
            total_attach_num = g.db.cur.fetchone()[0]
        else:
            total_attach_num = 0

        # 添加文件下载地址
        for file_data in data:
            if file_data['private'] == 1:
                file_data['url'] = '{}/{}'.format(site_url, file_data['pathname'])
            elif file_data['private'] == 2:
                file_data['url'] = '{}{}'.format(site_url, url_for('get_private_file_view', private_file=file_data['filename']))
            else:
                return False, ''
            del file_data['pathname']
        
            # 添加缩略图下载地址
            if size_level:
                state, url = make_mini_photo(file_data['filename'], size_level)
                if state:
                    file_data['mini_url'] = url
                else:
                    file_data['mini_url'] = False

        return_data = {'list_data': data, 'total_attach_num': total_attach_num}

        return True, return_data
    except Exception:
        log.error(traceback.format_exc())
    return False, ''