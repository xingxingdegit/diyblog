from api.dbpool import with_db, select, with_redis
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from api.setting import get_setting
from flask import g
import logging
import traceback
from config import redis_setting_name
from config import redis_comm_list

log = logging.getLogger(__name__)


# 刚启动的时候删除redis里缓存的配置
@with_redis
def clear_setting():
    pass

@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
@with_db('write')
def set_setting(data):
    try:
        set_id = int(data['set_id'])
        set_key = data['set_key'].strip()
        set_value = data['set_value'].strip()
        up_data = {'value': set_value}
        where_data = {'id': set_id, 'key': set_key, 'status': 1}
        state = g.db.update('setting', values=up_data, where=where_data)
        if state[0]:
            if set_key in redis_comm_list:
                g.redis.hset(redis_setting_name, set_key, set_value)
            if state[1] == 1:
                return True, ''
            else:
                log.error(
                    'fund:set_setting|set_id:{}|set_key:{}|set_value:{}|update_num:{}|update number > 1'.format(
                        set_id, set_key, set_value, state[1]))
                return True, ''
    except Exception:
        log.error(traceback.format_exc())
    return False
                

@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth()
def get_one_setting(*, set_name=None, set_type=None):
    try:
        if set_type is None:
            set_value = get_setting(set_name)
            if set_value is not False:
                return True, set_value

        type_data = {
            'upload_file': ['upload_file_size', 'upload_file_ext', 'upload_file_mime'],
        }
        set_names = type_data[set_type]
        if set_name:
            set_names.append(set_name)
        set_values = get_setting(set_names)
        if set_values is not False:
            return True, set_values
    except Exception:
        log.error(traceback.format_exc())
    return False, ''


@admin_url_auth_wrapper('api')
@auth_mode('login')
@cors_auth('cookie')
@with_db('read')
def get_all_setting():
    try:
        data = g.db.select('setting', fields=['id', 'key', 'value'], where={'status': 1})
        if data[0] and data[1]:
            data_dict = {one['key']: {'set_id': one['id'], 'set_value': one['value']} for one in data[1][1]}
            return True, data_dict
    except Exception:
        log.error(traceback.format_exc())
    return False, ''




