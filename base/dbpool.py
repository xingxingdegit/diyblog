# 处理数据库连接。
import logging
import pymysql
import traceback
import config
import threading
import datetime
import time
from config import DATABASES

log = logging.getLogger(__name__)


def create_connect(database_name):
    database_conf = DATABASES[database_name]
    connect = pymysql.connect(
        host=database_conf['host'],
        port=database_conf['port'],
        user=database_conf['user'],
        password=database_conf['password'],
        charset=database_conf['charset'],
    )
    log.debug('database_name: {}|host: {}|port: {}|user: ***|password: ***|charset: {}|database connect already create'.format(
        database_name, database_conf['host'], database_conf['port'], database_conf['charset']))
    return connect


def init_connect():
    conn_keys = {}
    connect_all = {}
    connect_idle = {}
    usage_number = {}
    for database_name, database_conf in DATABASES.items():
        conn_max = database_conf['conn_max']
        conn_keys[database_name] = {
            '{:0{}}'.format(x, len(str(conn_max))) for x in range(conn_max)
        }
        usage_number[database_name] = 0
        for _ in range(database_conf['conn_min'] or 1):
            conn_key = conn_keys[database_name].pop()
            connect = create_connect(database_name)
            connect_all.setdefault(database_name, {})[conn_key] = connect
            connect_idle.setdefault(database_name, set()).add(conn_key)

    return conn_keys, connect_all, connect_idle, usage_number


def connect_limit():
    connect_limit = {}
    for database_name, database_conf in DATABASES.items():
        conn_max = database_conf['conn_max']
        conn_min = database_conf['conn_min']
        connect_limit[database_name] = {'conn_max': conn_max, 'conn_min': conn_min}
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
    __connect_limit = connect_limit()
    __conn_keys, __connect_all, __connect_idle, usage_number = init_connect()
    __connect_timeout = {}
    connect = None

    def __init__(self, database_name):
        if self.connect:
            return None

        self.database_name = database_name
        self.debug(True, True, False, True, info='before get connect')
        try:
            self.conn_key = self.__connect_idle[database_name].pop()
        except KeyError:
            idle = False
        else:
            idle = True
            self.connect = self.__connect_all[database_name][self.conn_key]

        if not idle:
            try:
                self.conn_key = self.__conn_keys[database_name].pop()
            except KeyError:
                """ log : 数据库连接数到达上限 """
                log.error(
                    "database_name: {}|usage_number: {}|conn_key is empty, database connect up limit".format(
                        database_name, self.usage_number[database_name]
                    )
                )
                log.error(traceback.format_exc())
                raise KeyError('database connect already get up limit') from None
            except Exception:
                """ log  异常错误 """
                log.error(traceback.format_exc())
                raise
            else:
                self.debug(True, True, True, True, info='begin create database connect')
                self.connect = create_connect(database_name)
                self.__connect_all[database_name][self.conn_key] = self.connect

        self.usage_number[database_name] += 1
        self.debug(True, True, True, True, info='already get connect')

    def __del__(self):
        if self.connect:
            self.close()

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def debug(self, idle=False, all=False, conn_key=False, usage_number=False, info=None):
        if config.DEBUG:
            format = []
            data_src = {}
            if idle:
                format.append('idle: {idle}')
                data_src['idle'] = self.__connect_idle[self.database_name]
            if all:
                format.append('all: {all}')
                data_src['all'] = self.__connect_all[self.database_name].keys()
            if conn_key:
                format.append('conn_key: {conn_key}')
                data_src['conn_key'] = self.conn_key
            if usage_number:
                format.append('usage_number: {usage_number}')
                data_src['usage_number'] = self.usage_number[self.database_name]
            if info:
                format.append('info: {info}')
                data_src['info'] = info
            log.debug('|'.join(format).format_map(data_src))

    def get(self):
        self.connect.ping()
        return self.connect

    def close(self):
        if len(self.__connect_idle[self.database_name]) + 1 > DATABASES[self.database_name]['conn_min']:
            self.__close()
        else:
            self.__connect_idle[self.database_name].add(self.conn_key)
            self.debug(True, True, True, True, info='connect already recovery')
        self.connect = None
        self.usage_number[self.database_name] -= 1

    def __close(self):
        try:
            self.connect.close()
            del self.__connect_all[self.database_name][self.conn_key]
            self.__conn_keys[self.database_name].add(self.conn_key)
            self.debug(True, True, True, True, info='connect already closed')

        except Exception:
            log.error(traceback.format_exc())



class WhereSql():
    def where(self, factor, logic='and'):
        """ factor is [[{key: value, key:value, ...}, '=', 'and'], 'and', [{key:value}, '=', 'and'], 'and', ...]
            单数索引都是条件，双数索引是两个索引之间的逻辑运算符。
            条件索引里面也是列表，有3项， 包含条件字典， 条件的运算符， 以及条件之间的逻辑运算符。
            条件运算符: =, !=, >=, >, <=, <, between, in, not in, like
        """
    pass

class GetConnect():
    def __init__(self, database_name):
        self.obj = DbConnectPool(database_name)
        self.conn = self.obj.get()
        self.cur = self.conn.cursor()
        self.columns = {}

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        self.conn.rollback()
        self.cur.close()
        self.obj.close()

    def set_db(self, dbname):
        self.conn.select_db(dbname)

    def begin(self):
        self.conn.begin()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def where(self, factor):
        where_sql = []
        for key, value in factor.items():
            if key == value:
                log.error('key: {}|value: {}|info: where key == value, query is end'.format(key, value))
                break
            if not key.strip():
                log.error('key: {}|value: {}|info: where key is empty, query is end'.format(key, value))
                break
            if value is None:
                where_sql.append('{} is null'.format(key))
            else:
                where_sql.append('{}="{}"'.format(key, value))
        else:
            return ' and '.join(where_sql)
        return False

    def select(self, table, fields='*', where=None):
        if where:
            where = self.where(where)
        else:
            log.error('fields: {}|where: {}|info: database select'.format(fields, where))
            return False

    def fields(self, table):
        """字段必须查，除了生成数据字典外，最重要的是判断where中的字段是否存在"""
        fields = self.columns.get(table)
        if fields:
            return fields
        sql = 'show columns from {};'.format(table)
        log.info('sql: {}'.format(sql))
        self.cur.execute(sql)
        fields = [i[0] for i in self.cur.fetchall()]
        self.columns[table] = fields
        return fields





start = datetime.datetime.now()
count = [0]
def test_connect():
    yy = DbConnectPool('read')
    conn = yy.get()
    yy.close()
    count[0] += 1
    if count[0] > 80:
        end = datetime.datetime.now()
        print((end - start).total_seconds())

for x in range(82):
    new_thread = threading.Thread(target=test_connect)
    new_thread.start()
    


    
    
    
