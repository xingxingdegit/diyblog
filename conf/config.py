#
from pathlib import Path

basedir = Path(__file__).absolute().parent.parent

log_file = basedir / 'log/access.log'
err_file = basedir / 'log/error.log'

DEBUG = False

listen = {
    'host': '0.0.0.0',
    'port': 5000,
}
REDIS = {
    'host': '172.100.102.70',
    'port': 6379,
    'password': '',
    'db': 0
}

DATABASES = {
    'setting': {
        'dbname': 'diyblog',  # 使用的库
        'del_number': 10,   # 删除操作每次最多删除10条。 

    },
    'read': {                 #  select
        'host': '172.100.102.70',
        'port': 3306,
        'user': 'diyblog-read',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 20,    # 每个数据库服务器最大连接
        'conn_min': 1,     # 每个数据库服务器最少连接, 初始化的时候就自动创建了。回收连接的时候保留的空闲连接,最小是1，写0也是1。
        'conn_timeout': 600,     # 一个连接一直在使用，超过这么长时间没有回收， 则强制中断。 暂时没有使用
    },
    'write': {                # select, insert, create, update
        'host': '172.100.102.70',
        'port': 3306,
        'user': 'diyblog-write',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 10,
        'conn_min': 1,
        'conn_timeout': 600,
    },
    'delete': {              # select, delete
        'host': '172.100.102.70',
        'port': 3306,
        'user': 'diyblog-delete',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 5,
        'conn_min': 1,
    },
}

try:
    from config_local import *
except Exception:
    pass
