from api.dbpool import with_db, select, with_redis
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from flask import g
import logging
import traceback
import datetime
import os
from PIL import Image, UnidentifiedImageError
from config import basedir
from config import site_url

log = logging.getLogger(__name__)

def get_mini_photo(data):
    try:
        filename = data['filename']
        size_level = data['size_level']
        level = {1: (64, 64), 2: (128, 128), 3: (256, 256)}
        file_info = select('attach', fields=['pathname', 'mimetype', 'is_image'], where={'filename': filename, 'private': 1})[0]
        log.error(file_info)
        if file_info:
            pathname = file_info['pathname']
            is_image = file_info['is_image']
            if is_image:
                mini_file_pathname = os.path.dirname(pathname) + '/_{}_{}'.format(level[size_level][0], filename)
                url_path = '{}/{}'.format(site_url, mini_file_pathname)
                src_file_pathname = basedir / pathname
                dest_file_pathname = basedir / mini_file_pathname
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


def get_attach_list(data):
    try:
        pass
    except Exception:
        log.error(traceback.format_exc())
    return False, ''