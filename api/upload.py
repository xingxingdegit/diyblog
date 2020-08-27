from api.dbpool import with_db
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from api.setting import get_setting
from flask import g
import logging
import traceback
import datetime
import random
from config import site_url
from config import basedir
from pathlib import Path

log = logging.getLogger(__name__)

@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth('cookie')
@with_db('write')
def upload_file(files, file_size):
    try:
        return_data = {}
        filenames = []
        for pos in files:
            now = datetime.datetime.now()
            ext_name = files[pos].filename.split('.')[-1]
            mimetype = files[pos].mimetype
            first_type, _ = mimetype.split('/')
            setting = get_setting(['upload_file_ext', 'upload_file_size', 'upload_file_mime'])
            if ext_name not in setting['upload_file_ext'].split(','):
                log.error('fund:upload_file|ext_name:{}|ext_name not in setting'.format(ext_name))
                break
            if file_size == 0 or file_size > int(setting['upload_file_size']):
                log.error('fund:upload_file|file_size:{}|file size > setting'.format(file_size))
                break
            if first_type not in setting['upload_file_mime'].split(','):
                log.error('fund:upload_file|file_mime:{}|master mime not in setting'.format(first_type))
                break

            filename = first_type + '-'
            for i in str(now.timestamp()).replace('.', ''):
                filename += i + random.choice('abcdefghigklmnopqrstuvwxyz')
            while filename in filenames:
                filename += random.choice('abcdefghigklmnopqrstuvwxyz')
            filename += '.{}'.format(ext_name)
            filenames.append(filename)

            save_path = Path('static/upload') / '{}'.format(now.year) / '{:02}'.format(now.month) / filename
            system_path = basedir / save_path
            system_path.parent.mkdir(parents=True, exist_ok=True)
            log.error(system_path)
            db_data = {'filename': filename, 'pathname': str(save_path), 
                       'mimetype': mimetype, 'size': file_size, 'uptime': int(now.timestamp())}
            g.db.begin()
            state = g.db.insert('attach', db_data)
            if state[0]:
                try:
                    files[pos].save(system_path)
                except Exception:
                    log.error(traceback.format_exc())
                    g.db.rollback()
                else:
                    g.db.commit()
                    url_path = '{}/{}'.format(site_url, save_path)
                    return_data[pos] = url_path.replace('\\', '/')

# 这里会导致没有上传任何东西也会返回True
#        else:
#            return True, return_data
        
    except Exception:
        log.error(traceback.format_exc())
    # 便于以后修改， 先这样写
    # 只要return_data不是空的，就返回true， 表示批量上传中成功上传一点是一点。
    if return_data:
        return True, return_data
    else:
        return False, ''