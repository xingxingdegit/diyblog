#
from pathlib import Path

basedir = Path(__file__).absolute().parent.parent

log_file = basedir / 'log/access.log'
err_file = basedir / 'log/error.log'

DEBUG = False

# 加密cookie， cookie里面需要加密的只有用户名和对应的sessionID。
secret_key = b'''K\t\x91;\x9d8\n\xd8\xac\x97\xec(`\x0e$\x9a'''

listen = {
    'host': '0.0.0.0',
    'port': 5000,
}
REDIS = {
    'host': '172.17.221.213',
    'port': 6379,
    'password': 'mydiy',
    'db': 0
}

DATABASES = {
    'database': 'diyblog',   # 使用的库
    'read': {
        'host': '172.17.221.213',
        'port': 3306,
        'user': 'sst',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 50,    # 每个数据库服务器最大连接
        'conn_min': 0,     # 每个数据库服务器最少连接, 初始化的时候就自动创建了。回收连接的时候保留的空闲连接
        'conn_timeout': 600,     # 一个连接一直在使用，超过这么长时间没有回收， 则强制中断。 暂时没有使用
    },
    'write': {
        'host': '172.17.221.213',
        'port': 3306,
        'user': 'star',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 20,
        'conn_min': 0,
        'conn_timeout': 600,
    },
    'delete': {
        'host': '172.17.221.213',
        'port': 3306,
        'user': 'star',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 20,
        'conn_min': 0,
    },
}


