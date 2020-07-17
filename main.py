import eventlet
eventlet.monkey_patch()
import logging
import sys
from pathlib import Path
#from flask_socketio import SocketIO
sys.path.append(str(Path(__file__).absolute().parent / 'conf'))
from config import listen
# 加载一些初始化的模块
from api import logger
from api import dbpool
#
from route import socketio, app

''' 
python version: 3.8.2
'''

if __name__ == '__main__':
    socketio.run(app, host=listen['host'], port=listen['port'])


