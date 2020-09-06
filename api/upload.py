from api.dbpool import with_db
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from api.setting import get_setting
from flask import g, url_for
import logging
import traceback
import datetime
import random
from config import site_url
from config import basedir
from config import private_data_dir
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from io import BytesIO

log = logging.getLogger(__name__)

@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth('cookie')
@with_db('write')
def upload_file(files, file_size, other_data):
    try:
        return_data = {}
        filenames = []
        for pos in files:
            now = datetime.datetime.now()
            private = int(other_data.get('private', 1))
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
                log.error('fund:upload_file|file_mime:{}|first mime not in setting'.format(first_type))
                break

            filename = first_type + '-'
            for i in str(now.timestamp()).replace('.', ''):
                filename += i + random.choice('abcdefghigklmnopqrstuvwxyz')
            while filename in filenames:
                filename += random.choice('abcdefghigklmnopqrstuvwxyz')
            filename += '.{}'.format(ext_name)
            filenames.append(filename)

            if private == 1:
                save_path = Path('static/upload') / '{}'.format(now.year) / '{:02}'.format(now.month) / filename
                system_path = basedir / save_path
            elif private == 2:
                save_path = Path() / '{}'.format(now.year) / '{:02}'.format(now.month) / filename
                system_path = basedir / private_data_dir / save_path
            else:
                return False, ''
            system_path.parent.mkdir(parents=True, exist_ok=True)

            db_data = {'filename': filename, 'pathname': str(save_path).replace('\\', '/'), 'private': private, 
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
                    if private == 2:
                        url_path = '{}{}'.format(site_url, url_for('get_private_file_view', private_file=filename))
                    else:
                        url_path = '{}/{}'.format(site_url, save_path)
                    return_data[pos] = url_path.replace('\\', '/')
            try:
                im = Image.open(system_path)
            except UnidentifiedImageError:
                image_width, image_height = (0, 0)
                is_image = 2
            else:
                image_width, image_height = im.size
                is_image = 1
            finally:
                try:
                    im.close()
                except UnboundLocalError:
                    pass
            
            db_data = {'width': image_width, 'height': image_height, 'is_image': is_image}
            g.db.update('attach', db_data, where={'filename': filename})
            

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