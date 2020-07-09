# 处理数据库连接。
import logging
import pymysql
import traceback
import config
import threading
import datetime
import time
from config import DATABASES
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
    log.info('database_tag: {}|host: {}|port: {}|user: ***|password: ***|charset: {}|database connect already create'.format(
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
    param: connect_all {database_name: {conn_key: connect_obj}, ...}   all of connect.
    param: connect_idle {database_name: {conn_key, conn_key, ...}  idle of connect.
    param: conn_keys {database_name: {*, *, *, ...}
    conn_key 是同一服务器的不同连接的名称。 为了把connect_all与connect_idle的连接对应起来
    param: usage_number   记录使用数据库的实例数量
    param: connect_limit  {database_name: {'conn_max': #, 'conn_min': #}},  之后做一些完整性判断，暂时没有使用。
    param: connect_timeout   超过时间还没有close的连接，强制close， 暂时还不知道怎么实现比较好.
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
        if self.__connect_idle[database_tag]:
            self.conn_key = self.__connect_idle[database_tag].pop()
            self.connect = self.__connect_all[database_tag][self.conn_key]
        else:
            if self.__conn_keys[database_tag]:
                self.conn_key = self.__conn_keys[database_tag].pop()
                self.log(True, True, True, True, info='begin create database connect')
                self.connect = create_connect(database_tag)
                self.__connect_all[database_tag][self.conn_key] = self.connect

            else:
                """ log : 数据库连接数到达上限 """
                log.error(
                    "database_tag: {}|usage_number: {}|conn_key is empty, database connect up limit".format(
                        database_tag, self.usage_number[database_tag]
                    )
                )
                log.error(traceback.format_exc())
                raise KeyError('database connect already get up limit') from None

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
            format.append('idle: {idle}')
            data_src['idle'] = self.__connect_idle[self.database_tag]
        if all:
            format.append('all: {all}')
            data_src['all'] = self.__connect_all[self.database_tag].keys()
        if conn_key:
            format.append('conn_key: {conn_key}')
            data_src['conn_key'] = self.conn_key
        if usage_number:
            format.append('usage_number: {usage_number}')
            data_src['usage_number'] = self.usage_number[self.database_tag]
        if info:
            format.append('info: {info}')
            data_src['info'] = info
        log.info('|'.join(format).format_map(data_src))

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
        self.conn.begin()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def where(self, where, fields):
        where_sql = []
        if where:
            for key, value in where.items():
                # 防止1==1的条件出现，添加字段判断以后就不需要了。
                #if key == value:
                #    log.error('key: {}|value: {}|info: where key == value, query is end'.format(key, value))
                #    break
                # 防止空key。
                if not key.strip():
                    log.error('key: {}|value: {}|info: where key is empty, query is end'.format(key, value))
                    break
                # key没有在表字段里
                if key not in fields:
                    log.error('key: {}|value: {}|info: where key is not in fields, query is end'.format(key, value))
                    break
                if value is None:
                    where_sql.append('{} is null'.format(key))
                else:
                    where_sql.append('{}="{}"'.format(key, value))
            else:
                return ' and '.join(where_sql)
        return False


    def fields(self, table):
        """字段必须查，除了生成数据字典外，最重要的是判断where中的字段是否存在"""
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

    def select(self, table, fields='*', where=None, return_data=True):
        all_fields = self.fields(table)
        if not all_fields:
            return False, None

        if fields == '*':
            fields = ','.join(all_fields)

        whsql = self.where(where, all_fields)
        if whsql:
            sql = r'select {} from {} where {};'.format(fields, table, whsql)
        else:
            log.error('op: select|fields: {}|where: {}|info: where check fail'.format(fields, where))
            return False, None

        log.info('op:select|sql: {}'.format(sql))
        number = self.cur.execute(sql)
        if return_data:
            return_data = number, [dict(zip(fields.split(','), onedata)) for onedata in self.cur.fetchall()]
        else:
            return_data = number
        return True, return_data

    def insert(self, table, value):
        all_fields = self.fields(table)
        if not all_fields:
            return False, None

        if not isinstance(value, list):
            value = [value]

        number = 0
        for one_data in value:
            if set(one_data.keys()) - all_fields:
                log.error('op:insert|table:{}|value:{}|info:fields not in table'.format(table, value))
                return False, None
            values = ','.join(['"{}"'] * len(one_data)).format(*one_data.values())
            keys = ','.join(['{}'] * len(one_data)).format(*one_data.keys())
            sql = r'insert into {} ({}) values ({});'.format(table, keys, values)
            try:
                number += self.cur.execute(sql)
            except Exception:
                log.error(traceback.format_exc())
                self.conn.rollback()
                break
        else:
            self.conn.commit()
            return True, number
        return False, None

    def query(self, sql):
        try:
            data = self.cur.execute(sql)
        except Exception:
            self.conn.rollback()
            log.error(traceback.format_exc())
            return False, None
        else:
            self.conn.commit()
            return True, data

    def update(self, table, values, where):
        all_fields = self.fields(table)
        if not all_fields:
            return False, None

        setsql = []
        for key, value in values.items():
            if value == None:
                setsql.append('{}=null'.format(key))
            else:
                setsql.append('{}="{}"'.format(key, value))
        setsql = ','.join(setsql)
        whsql = self.where(where, all_fields)
        if whsql:
            sql = 'update {} set {} where {};'.format(table, setsql, whsql)
        else:
            log.error('op: update|where: {}|info: where check fail'.format(where))
            return False, None

        log.info('op:update|sql: {}'.format(sql))
        try:
            data = self.cur.execute(sql)
        except:
            self.conn.rollback()
            log.error(traceback.format_exc())
            return False, None
        else:
            log.info('update number is: {}'.format(data))
            self.conn.commit()
            return True, data

    def delete(self, table, where):
        number = self.select(table, where=where, return_data=False)
        if number[0]:
            return False, None

        max_del_number = DATABASES['setting']['del_number']
        if number[1] == 0 or number[1] > max_del_number:
            log.error(
                'op: delete|table:{}|where:{}|del_number: {}|info:check "Number of records deleted is error"'.format(table, where, number)
            )
            return False, None

        all_fields = self.fields(table)
        if not all_fields:
            return False, None
        whsql = self.where(where, all_fields)
        if whsql:
            sql = 'delete from {} where {};'.format(table, whsql)
        else:
            log.error('op: delete|where: {}|info: where check fail'.format(where))
            return False, None
        log.info('op:delete|sql: {}'.format(sql))
        try:
            number = self.cur.execute(sql)
        except:
            self.conn.rollback()
            log.error(traceback.format_exc())
            return False, None
        else:
            if number > max_del_number:
                self.conn.rollback()
                log.error('op:delete|del_number:{}|info: Beyond Max Number, already rollback'.format(number))
                return False, None
            else:
                log.info('delete number is: {}'.format(number))
                self.conn.commit()
                return True, number



def with_database(tag):
    def inner(func):
        from flask import g
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with DbGetConnect(tag) as g.db:
                data = func(*args, **kwargs)
            return data
        return wrapper
    return inner


#start = datetime.datetime.now()
#count = [0]
#def test_connect():
#    yy = DbConnectPool('read')
#    conn = yy.get()
#    yy.close()
#    count[0] += 1
#    if count[0] > 60:
#        end = datetime.datetime.now()
#        print((end - start).total_seconds())
#
#for x in range(82):
#    new_thread = threading.Thread(target=test_connect)
#    new_thread.start()
    


    
# 初始化表
def create_table():
    posts_sql = r'''
                CREATE TABLE IF NOT EXISTS `posts` (
                `id` int(10) unsigned NOT NULL,
                `title` varchar(100) NOT NULL,
                `create_time` int(10) unsigned NOT NULL,
                `update_time` int(10) unsigned NOT NULL,
                `posts` longtext DEFAULT NULL,
                `class` tinyint(3) unsigned DEFAULT NULL,
                `status` tinyint(3) unsigned NOT NULL,
                `visits` int(10) unsigned DEFAULT NULL,
                `urls` varchar(100) DEFAULT NULL,
                `istop` tinyint(4) DEFAULT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8
              '''
    class_sql = r'''
                CREATE TABLE IF NOT EXISTS `class` (
                `id` int(10) unsigned NOT NULL,
                `classname` varchar(100) NOT NULL,
                `status` tinyint(4) NOT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8
              '''
    tags_sql = r'''
              CREATE TABLE IF NOT EXISTS `tags` (
                `id` int(10) unsigned NOT NULL,
                `tagname` varchar(100) NOT NULL,
                `post` int(10) unsigned NOT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8
              '''
    users_sql = r'''
                CREATE TABLE IF NOT EXISTS `users` (
                `id` int(10) unsigned NOT NULL,
                `username` varchar(100) NOT NULL,
                `password` varchar(100) NOT NULL,
                `role` tinyint(4) NOT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8
              '''

    with DbGetConnect() as db:
        p = db.query(posts_sql)
        c = db.query(class_sql)
        t = db.query(tags_sql)
        u = db.query(users_sql)
    if p[0] and c[0] and t[0] and u[0]:
        print(p[1], c[1], t[1], u[1])
        return True
    else:
        return False

    
