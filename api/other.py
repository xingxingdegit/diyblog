from flask import url_for
from api.dbpool import select
from api.setting import get_setting
from api.auth import admin_url_auth_wrapper
import traceback
import logging

log = logging.getLogger(__name__)

@admin_url_auth_wrapper('api')
def get_url(r_type):
    type_data = {'login': 'admin_login_page', 'get_post_list': 'get_post_list_view'}
    try:
        url_type = type_data[r_type]
        admin_url = get_setting('admin_url')
        login_url = url_for(url_type, admin_url=admin_url)
        return True, login_url
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


