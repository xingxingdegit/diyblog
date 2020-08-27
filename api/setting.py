from api.dbpool import with_db, select, with_redis
from flask import g
import logging
import traceback

log = logging.getLogger(__name__)

@with_redis
def get_setting(set_names):
    ''' param: set_names  :   str or list
        return_data:  dict
    '''
    # 存储配置的redis key
    redis_setting_name = 'diyblog_setting_common'
    # 可以存redis的配置
    comm_list = {'admin_url', 'user_timeout', 'sitename', 'avatar_url', 'upload_file_size', 'upload_file_ext', 'upload_file_mime'}

    simple = False
    if not isinstance(set_names, list):
        simple = set_names
        set_names = [set_names]

    all_set_names = set(set_names)
    redis_set_names = all_set_names & comm_list
    db_set_names = all_set_names - redis_set_names
    data = {}
    try:
        for set_name in redis_set_names:
            value = g.redis.hget(redis_setting_name, set_name)
            if value:
                data[set_name] = value
            else:
                db_set_names.add(set_name)
    
        redis_empty_set = db_set_names & redis_set_names
        if db_set_names:
            db_data = select('setting', fields=['key', 'value'], where={'key': list(db_set_names)})
            if db_data: 
                for one_set in db_data:
                    key = one_set['key']
                    try:
                        value = int(one_set['value'])
                    except ValueError:
                        value = one_set['value']
                    data[key] = value
                    if key in redis_empty_set:
                        g.redis.hset(redis_setting_name, key, value)
            else:
                log.error('func:{}|settings:{}|set not found'.format('get_setting', ','.join(db_set_names)))
    
        if simple:
            return data[simple]
        return data
    except Exception:
        log.error(traceback.format_exc())
        return False



                



