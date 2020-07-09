#
from pathlib import Path

basedir = Path(__file__).absolute().parent.parent

log_file = basedir / 'log/access.log'
err_file = basedir / 'log/error.log'

DEBUG = False

user_timeout = 36000  # 秒， 登录以后长时间没有操作的超时时间。超时以后需要重新登陆。
login_prefix_key_timeout = 300  # 秒， 登录界面获取的安全key超市时间， 这个key与用户名密码共同组成登录验证。

# 加密cookie， cookie里面需要加密的只有用户名和对应的sessionID。
secret_key = b'''K\t\x91;\x9d8\n\xd8\xac\x97\xec(`\x0e$\x9a'''

listen = {
    'host': '0.0.0.0',
    'port': 5000,
}
REDIS = {
    'host': '172.17.221.213',
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
        'host': '172.17.221.213',
        'port': 3306,
        'user': 'diyblog-read',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 20,    # 每个数据库服务器最大连接
        'conn_min': 1,     # 每个数据库服务器最少连接, 初始化的时候就自动创建了。回收连接的时候保留的空闲连接,最小是1，写0也是1。
        'conn_timeout': 600,     # 一个连接一直在使用，超过这么长时间没有回收， 则强制中断。 暂时没有使用
    },
    'write': {                # select, insert, create
        'host': '172.17.221.213',
        'port': 3306,
        'user': 'diyblog-write',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 10,
        'conn_min': 1,
        'conn_timeout': 600,
    },
    'delete': {              # select, insert, delete
        'host': '172.17.221.213',
        'port': 3306,
        'user': 'diyblog-delete',
        'password': 'abcdefg',
        'charset': 'utf8',
        'conn_max': 5,
        'conn_min': 1,
    },
}


