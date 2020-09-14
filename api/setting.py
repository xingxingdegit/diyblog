from api.dbpool import select, with_redis, RedisGetConnect
from flask import g
import logging
import traceback
from config import redis_setting_name
from config import redis_comm_list

log = logging.getLogger(__name__)



# 刚启动的时候删除redis里缓存的配置
def clear_setting():
    redis = RedisGetConnect()
    return redis.delete(redis_setting_name)

clear_setting()


@with_redis
def get_setting(set_names):
    ''' param: set_names  :   str or list
        return_data:  dict
    '''
    simple = False
    if not isinstance(set_names, list):
        simple = set_names
        set_names = [set_names]

    all_set_names = set(set_names)
    redis_set_names = all_set_names & redis_comm_list
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
