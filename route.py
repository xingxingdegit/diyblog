from flask import Flask
from flask_socketio import SocketIO, send, emit
from config import secret_key
import logging
# app func
from view import hello
from view.login import login
from view.init import init
from view.init import test_socket
from view.init import test_socket1
from view.init import message
from view.init import json_data

##########################################################

log = logging.getLogger(__name__)

app = Flask('diyblog')
app.secret_key = secret_key
app.debug = False
socketio = SocketIO(app)
socketio.server.eio.async_mode = 'eventlet'

##########################################################


#####################################
import time
def tttt():
    log.info('tttt: {}'.format(1111111))
    socketio.send('1111111111')
#    send('1111111111')
    return '11111111111'

# url
app.add_url_rule(rule='/hello', view_func=hello.hello, methods=['GET'])
app.add_url_rule(rule='/login', view_func=login, methods=['POST', 'GET'])
app.add_url_rule(rule='/init', view_func=init, methods=['POST'])
app.add_url_rule(rule='/test', view_func=hello.test_form, methods=['GET','POST'])


# websocket event
socketio.on_event('my event', handler=test_socket)
socketio.on_event('connect', handler=test_socket1)
socketio.on_event('message', handler=message)
socketio.on_event('json', handler=json_data)