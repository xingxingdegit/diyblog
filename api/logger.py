import logging
import config
from logging.handlers import RotatingFileHandler
import functools
from flask import request, Response


log_file = config.log_file
err_file = config.err_file

DEBUG = config.DEBUG

formatter = logging.Formatter(
#    fmt='%(asctime)s|%(name)s|%(levelname)s|Process:%(process)d|Thread:%(thread)d|%(message)s',
    fmt='%(asctime)s|%(levelname)s|Process:%(process)d|Thread:%(thread)d|%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(formatter)

err_handler = RotatingFileHandler(err_file, encoding='utf-8', maxBytes=1000000000, backupCount=3)
err_handler.setLevel(logging.ERROR)
err_handler.setFormatter(formatter)

log_handler = RotatingFileHandler(log_file, encoding='utf-8', maxBytes=1000000000, backupCount=3)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(formatter)

root = logging.getLogger()

root.addHandler(err_handler)
root.addHandler(log_handler)

if DEBUG:
    root.setLevel(logging.DEBUG)
    root.addHandler(stream)
else:
    root.setLevel(logging.INFO)



log = logging.getLogger(__name__)

def base_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        try:
            status = data.status_code
        except AttributeError:
            if data:
                status = data[0]
            else:
                status = ''
        log.info('func:{}|addr:{}|method:{}|url:{}|rep_status:{}'.format(func.__name__, request.remote_addr, request.method, request.url, status))
        return data
    return wrapper
