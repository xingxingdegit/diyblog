# 处理数据库连接。
import logging
import pymysql
import redis
import traceback
import config
import datetime
from config import DATABASES
from config import REDIS
import functools

log = logging.getLogger(__name__)


def create_connect(database_tag):
    database_conf = DATABASES[database_tag]
    connect = pymysql.connect(
        host=database_conf['host'],
        port=database_conf['port'],
        database=DATABASES['setting']['dbname'],
        user=database_conf['user'],
        password=database_conf['password'],
        charset=database_conf['charset'],
        autocommit=False,
    )
    log.debug('database_tag: {}|host: {}|port: {}|user: ***|password: ***|charset: {}|database connect already create'.format(
        database_tag, database_conf['host'], database_conf['port'], database_conf['charset']))
    return connect


def init_connect():
    conn_keys = {}
    connect_all = {}
    connect_idle = {}
    usage_number = {}
    for database_tag, database_conf in DATABASES.items():
        if database_tag == 'setting':
            continue
        conn_max = database_conf['conn_max']
        conn_keys[database_tag] = {
            '{:0{}}'.format(x, len(str(conn_max))) for x in range(conn_max)
        }
        usage_number[database_tag] = 0
        for _ in range(database_conf['conn_min'] or 1):
            conn_key = conn_keys[database_tag].pop()
            connect = create_connect(database_tag)
            connect_all.setdefault(database_tag, {})[conn_key] = connect
            connect_idle.setdefault(database_tag, set()).add(conn_key)

    return conn_keys, connect_all, connect_idle, usage_number


def connect_limit():
    connect_limit = {}
    for database_tag, database_conf in DATABASES.items():
        conn_max = database_conf['conn_max']
        conn_min = database_conf['conn_min']
        connect_limit[database_tag] = {'conn_max': conn_max, 'conn_min': conn_min}
    return connect_limit


class DbConnectPool:
    """
    param: connect_all {database_tag: {conn_key: connect_obj}, ...}   all of connect.
    param: connect_idle {database_tag: {conn_key, conn_key, ...}  idle of connect.
    param: conn_keys {database_tag: {*, *, *, ...}
    conn_key 是同一服务器的不同连接的名称。 为了把connect_all与connect_idle的连接对应起来
    param: usage_number   记录使用数据库的实例数量
    param: connect_limit  {database_tag: {'conn_max': #, 'conn_min': #}},  之后做一些完整性判断，暂时没有使用。
    param: connect_timeout   超过时间还没有close的连接，强制close， 暂时还不知道怎么实现比较好.
    """
    """
    log:
    use_conn_key: 当前使用的conn_key。
    all_conn_key: 所有可以用来创建连接的conn_key。
    all_conn: 所有连接的conn_key，包括空闲的与正在使用的。
    idle_conn: 空闲连接的conn_key。
    usage_numbe: 多少连接在被使用。
    connect already recovery:  连接已经回收到idle_conn。
    connect already closed：连接已经关闭，回收conn_key到all_conn_key。
    """
    __conn_keys, __connect_all, __connect_idle, usage_number = init_connect()
    #__connect_limit = connect_limit()
    #__connect_timeout = {}
    connect = None

    def __init__(self, database_tag):
        if self.connect:
            return None
        self.database_tag = database_tag
        self.log(True, True, False, True, info='before get connect')
        try:
        # 多线程环境无法确定容器里是否还有值
            self.conn_key = self.__connect_idle[database_tag].pop()
            self.connect = self.__connect_all[database_tag][self.conn_key]
        except KeyError:
            log.debug(traceback.format_exc())
            try:
                self.conn_key = self.__conn_keys[database_tag].pop()
                self.log(True, True, True, True, info='begin create database connect')
            except KeyError:
                """ log : 数据库连接数到达上限 """
                log.error(
                    "database_tag: {}|usage_number: {}|conn_key is empty, database connect up limit".format(
                        database_tag, self.usage_number[database_tag]))
                log.error(traceback.format_exc())
                raise KeyError('database connect already get up limit') from None
            else:
                self.connect = create_connect(database_tag)
                self.__connect_all[database_tag][self.conn_key] = self.connect
        self.usage_number[database_tag] += 1
        self.log(True, True, True, True, info='already get connect')

    def __del__(self):
        if self.connect:
            self.close()

    def __enter__(self):
        return self.get()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()
        if exc_type is not None:
            log.error(traceback.format_exc())


    def log(self, idle=False, all=False, conn_key=False, usage_number=False, info=None):
        format = []
        data_src = {}
        if idle:
            format.append('idle_conn:{idle}')
            data_src['idle'] = ','.join(self.__connect_idle[self.database_tag])
        if all:
            format.append('all_conn:{all}')
            data_src['all'] = ','.join(self.__connect_all[self.database_tag].keys())
        if conn_key:
            format.append('all_conn_key:{all_conn_key}')
            data_src['all_conn_key'] = ','.join(self.__conn_keys[self.database_tag])
            format.append('use_conn_key:{use_conn_key}')
            data_src['use_conn_key'] = self.conn_key
        if usage_number:
            format.append('usage_number:{usage_number}')
            data_src['usage_number'] = self.usage_number[self.database_tag]
        if info:
            format.append('info:{info}')
            data_src['info'] = info
        log.debug('|'.join(format).format_map(data_src))

    def get(self):
        self.connect.ping()
        return self.connect

    def close(self):
        if len(self.__connect_idle[self.database_tag]) + 1 > DATABASES[self.database_tag]['conn_min']:
            self.__close()
        else:
            self.__connect_idle[self.database_tag].add(self.conn_key)
            self.log(True, True, True, True, info='connect already recovery')
        self.connect = None
        self.usage_number[self.database_tag] -= 1
        self.isclose = True

    def __close(self):
        try:
            self.connect.close()
            del self.__connect_all[self.database_tag][self.conn_key]
            self.__conn_keys[self.database_tag].add(self.conn_key)
            self.log(True, True, True, True, info='connect already closed')

        except Exception:
            log.error(traceback.format_exc())



class WhereSql():
    def where(self, where, logic='and'):
        """ factor is [[{key: value, key:value, ...}, '=', 'and'], 'and', [{key:value}, '=', 'and'], 'and', ...]
            单数索引都是条件，双数索引是两个索引之间的逻辑运算符。
            条件索引里面也是列表，有3项， 包含条件字典， 条件的运算符， 以及条件之间的逻辑运算符。
            条件运算符: =, !=, >=, >, <=, <, between, in, not in, like
        """
    pass

class DbGetConnect():
    isclose = False
    columns = {}
    auto_commit = True   # 只是内部控制的自动提交， 不是数据库的自动提交
    def __init__(self, database_tag='read'):
        self.obj = DbConnectPool(database_tag)
        self.conn = self.obj.get()
        self.cur = self.conn.cursor()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()
        if exc_type is not None:
            log.error(traceback.format_exc())

    def __del__(self):
        if not self.isclose:
            self.close()

    def close(self):
        self.rollback()
        self.cur.close()
        self.obj.close()
        self.isclose = True

    def begin(self):
        self.auto_commit = False
        self.conn.begin()

    def commit(self):
        self.auto_commit = True
        self.conn.commit()

    def rollback(self):
        self.auto_commit = True
        self.conn.rollback()

    def where(self, where, fields):
        """
            ::param where: {key: value, ..., key: [value, value,...], ...}
            ::param fields: [<field>, ...]
        """
        where_sql = []
        if where:
            for key, value in where.items():
                # 防止1==1的条件出现，添加字段判断以后就不需要了。
                #if key == value:
                #    log.error('key: {}|value: {}|info: where key == value, query is end'.format(key, value))
                #    break
                # 防止空key。
                if not key.strip():
                    log.error('key:{}|value:{}|info:where key is empty'.format(key, value))
                    break
                # key没有在表字段里
                if key not in fields:
                    log.error('key:{}|value:{}|info:where key is not in fields'.format(key, value))
                    break
                if (value is True) or (value is False) or (value == []):
                    log.error('key:{}|value:{}|info:value have a question'.format(key, value))
                    break

                if not isinstance(value, list):
                    value = [value]
                or_term = []
                for one_value in value:
                    if one_value is None:
                        or_term.append('`{}` is null'.format(key))
                    else:
                        or_term.append('`{}`="{}"'.format(key, pymysql.escape_string(str(one_value))))
                if len(or_term) > 1:
                    or_term = '({})'.format(' or '.join(or_term))
                else:
                    or_term = or_term[0]

                where_sql.append(or_term)
            else:
                log.debug('func:where|where_sql:{}'.format(where_sql))
                return ' and '.join(where_sql)
        return False


    def fields(self, table):

        """字段必须查，除了生成数据字典外，最重要的是判断where中的字段是否存在
           params: return_data:  [<field>, ...]
        """
        fields = self.columns.get(table)
        if fields:
            return fields

        sql = r'show columns from {};'.format(table)
        log.info('sql: {}'.format(sql))
        try:
            self.cur.execute(sql)
        except Exception:
            log.error(traceback.format_exc())
            return False

        fields = {i[0] for i in self.cur.fetchall()}
        self.columns[table] = fields
        return fields

    def select(self, table, fields='*', *, where=None, sort_field=None, sort_type='desc', limit=None, offset=0):
        """ ::param fields: [] 
            ::param where: {key: value, ..., key: [value, value,...], ...}
            ::param sort_field: table field name
            ::param sort_type: sort type,  desc or asc
            ::return data: (<state>, (<number>, [{},{},...]))
        """
        all_fields = self.fields(table)
        if not all_fields:
            return False, None
        if fields == '*':
            fields_list = all_fields
            fields = ','.join(['`{}`'] * len(all_fields)).format(*all_fields)
        elif isinstance(fields, list):
            fields_list = fields
            fields = ','.join(['`{}`'] * len(fields)).format(*fields)
        else:
            log.error('func:select|fields:{}|info:fields type is error')
            return False, None

        whsql = self.where(where, all_fields)
        if whsql:
            sql = r'select {} from `{}` where {}'.format(fields, table, whsql)
        else:
            log.error('func:select|fields:{}|where:{}|info:where check fail'.format(fields, where))
            return False, None
        
        if sort_field:
            if sort_field not in all_fields:
                log.error('func:select|sort_field:{}|info:sort_field not in field'.format(sort_field))
                return False, None
            if sort_type not in ('asc', 'desc'):
                log.error('func:select|sort_type:{}|info:sort_type is error'.format(sort_type))
                return False, None
            sql = r'{} order by `{}` {}'.format(sql, sort_field, sort_type)


        # 因为limit可能会是0, 所以不能直接判断limit真假.
        if limit is not None:
            sql = r'{} limit {}, {};'.format(sql, int(offset), int(limit))
        else:
            sql = r'{};'.format(sql)

        log.info('func:select|sql: {}'.format(sql))
        number = self.cur.execute(sql)
        return_data = number, [dict(zip(fields_list, onedata)) for onedata in self.cur.fetchall()]
        return True, return_data

    def insert(self, table, value):
        """
        :param: value:  {key: value, ...}  or  [{key: value,...}, {key: value,...}, ...]
        """
        all_fields = self.fields(table)
        if not all_fields:
            log.info('func:insert|all_fields get fail')
            return False, None

        if not isinstance(value, list):
            value = [value]

        number = 0
        for one_data in value:
            if set(one_data.keys()) - all_fields:
                log.error('func:insert|table:{}|value:{}|info:fields not in table'.format(table, value))
                return False, None
            keys = []
            values = []
            for key in one_data:
                keys.append('`{}`'.format(key))
                values.append('{{{}}}'.format(key))

            values = ','.join(values)
            keys = ','.join(keys)
            sql = r'''insert into `{}` ({}) values ({});'''.format(table, keys, values)
            sql = sql.format_map(pymysql.escape_dict(one_data, self.conn.charset))
            try:
                if len(sql) > 200:
                    log.info('func:insert|sql:insert into `{}` ({}) value (...)'.format(table, keys))
                else:
                    log.info('func:insert|sql:{}'.format(sql))
                number += self.cur.execute(sql)
            except Exception:
                log.error(traceback.format_exc())
                self.rollback()
                break
        else:
            if self.auto_commit:
                self.commit()
            return True, number
        return False, None

    def query(self, sql):
        try:
            log.info('func:query|sql: {}'.format(sql))
            data = self.cur.execute(sql)
        except Exception:
            self.rollback()
            log.error(traceback.format_exc())
            return False, None
        else:
            if self.auto_commit:
                self.commit()
            return True, data

    def update(self, table, values, *, where):
        """param: values:  {}
        """
        all_fields = self.fields(table)
        if not all_fields:
            return False, None

        setsql = []
        for key, value in values.items():
            if value == None:
                setsql.append('`{}`=null'.format(key))
            else:
                setsql.append('`{0}`= {{{0}}}'.format(key))
        setsql = ','.join(setsql)
        whsql = self.where(where, all_fields)
        if whsql:
            sql = 'update `{}` set {} where {};'.format(table, setsql, whsql)
        else:
            log.error('func:update|where:{}|info:where check fail'.format(where))
            return False, None

        sql = sql.format_map(pymysql.escape_dict(values, self.conn.charset))
        if len(sql) > 200:
            log.info('func:update|sql:update `{}` set ... where {};'.format(table, whsql))
        else:
            log.info('func:update|sql:{}'.format(sql))
        try:
            data = self.cur.execute(sql, values)
        except:
            self.rollback()
            log.error(traceback.format_exc())
            return False, None
        else:
            log.info('update number is: {}'.format(data))
            if self.auto_commit:
                self.commit()
            return True, data

    def delete(self, table, where):
        setting = self.select('setting', where={'key': 'del_number'})
        if setting[0]:
            if setting[1][0]:
                del_number = int(setting[1][1][0]['value'])
            else:
                log.error('func:delete|set:del_number|setting not found')
                return False, None
        else:
            return False, None
        number = self.select(table, where=where)
        if number[1][0] == 0 or number[1][0] > del_number:
            log.error(
                'func:delete|table:{}|where:{}|del_number:{}|info:check "Number of records deleted is error"'.format(table, where, number)
            )
            return False, None

        all_fields = self.fields(table)
        if not all_fields:
            return False, None
        whsql = self.where(where, all_fields)
        if whsql:
            sql = 'delete from `{}` where {};'.format(table, whsql)
        else:
            log.error('func:delete|where:{}|info:where check fail'.format(where))
            return False, None
        log.info('func:delete|sql: {}'.format(sql))
        try:
            number = self.cur.execute(sql)
        except:
            self.rollback()
            log.error(traceback.format_exc())
            return False, None
        else:
            if number > del_number:
                self.rollback()
                log.error('func:delete|del_number:{}|info: Beyond Max Number, already rollback'.format(number))
                return False, None
            else:
                log.info('delete number is: {}'.format(number))
                if self.auto_commit:
                    self.commit()
                return True, number




class RedisGetConnect:
    pool = redis.ConnectionPool(
        host=REDIS['host'], port=REDIS['port'], 
        password=REDIS['password'], db=REDIS['db'], decode_responses=True)
    
    def __init__(self):
        self.__connect = redis.Redis(connection_pool=self.pool)

    def set(self, key, value, ex=None):
        return self.__connect.set(key, value, ex)

    def get(self, key):
        return self.__connect.get(key)

    def delete(self, key):
        return self.__connect.delete(key)

    def expire(self, key, second):
        return self.__connect.expire(key, second)

    def ttl(self, key):
        return self.__connect.ttl(key)

    def hmset(self, key, value):
        return self.__connect.hmset(key, value)

    def hset(self, key, hkey, hvalue):
        return self.__connect.hset(key, hkey, hvalue)

    def hgetall(self, key):
        return self.__connect.hgetall(key)

    def hget(self, key, hkey):
        return self.__connect.hget(key, hkey)

    def hkeys(self, key):
        return self.__connect.hkeys(key)

    def hdel(self, key, *hkeys):
        return self.__connect.hdel(key, *hkeys)
    
    def ping(self):
        return self.__connect.ping()

    def rpush(self, key, *value):
        return self.__connect.rpush(key, *value)

    def rpushx(self, key, *value):
        return self.__connect.rpushx(key, *value)

    def lrange(self, key, *value):
        return self.__connect.lrange(key, *value)

    def lrem(self, key, count, value):
        return self.__connect.lrem(key, count, value)

    def lset(self, key, index, lvalue):
        return self.__connect.lset(key, index, value)


from flask import g

def with_db(tag):
    ''' 以装饰器的方式使用完整的db对象 '''
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            g.redis = RedisGetConnect()
            with DbGetConnect(tag) as g.db:
                return func(*args, **kwargs)
        return wrapper
    return inner

# 以函数的形式使用select查询，并且精简返回的数据
def select(table, fields='*', *args, return_query_number=False, **kwargs):
    with DbGetConnect('read') as db:
        try:
            data = db.select(table, fields, *args, **kwargs)
            if data[0]:
                if return_query_number:
                    return data[1]
                else:
                    return data[1][1]
            else:
                log.info('func:select|return_state:{}|info:select return have a error'.format(data[0]))
        except Exception:
            log.error(traceback.format_exc())
            return []



def with_redis(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        g.redis = RedisGetConnect()
        return func(*args, **kwargs)
    return wrapper


# 初始化检测redis是否可以连接
test_redis =  RedisGetConnect()
test_redis.ping()


# 只是测试 数据库代码
#start = datetime.datetime.now()
#count = [0]
#import time
#import threading
#def test_connect():
#    yy = DbConnectPool('read')
#    conn = yy.get()
#    time.sleep(2)
#    yy.close()
#    count[0] += 1
#    if count[0] > 60:
#        end = datetime.datetime.now()
#        print((end - start).total_seconds())
#
#for x in range(82):
#    new_thread = threading.Thread(target=test_connect)
#    new_thread.start()
    
