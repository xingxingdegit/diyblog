#
from pathlib import Path

basedir = Path(__file__).absolute().parent.parent

# Path type
log_file = basedir / 'log/access.log'
err_file = basedir / 'log/error.log'

# Path type,  不公开的图片存放位置, 系统的绝对路径, 也可以写相对路径.
#private_data_dir = 'data'           # 相对路径， 相对于项目的路径
#private_data_dir = '/data'
private_data_dir = 'G:/00000/data'
#########################


site_url = 'http://localhost:8080'   # 需要拼接url，  也跟安全认证有关,

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

# 用来缓存配置的redis key名称, 是个字典结构。
redis_setting_name = 'diyblog_setting_common'
# 可以缓存redis的配置项
redis_comm_list = {'admin_url', 'user_timeout', 'sitename', 'avatar_url', 'upload_file_size', 'upload_file_ext', 'upload_file_mime'}

try:
    from config_local import *
except Exception:
    pass
