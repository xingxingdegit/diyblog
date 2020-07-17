from flask import Flask
from flask_socketio import SocketIO, send, emit
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
app.debug = False
socketio = SocketIO(app)
socketio.server.eio.async_mode = 'eventlet'

##########################################################


#####################################

# url
app.add_url_rule(rule='/hello', view_func=hello.hello, methods=['GET'])
app.add_url_rule(rule='/login', view_func=login, methods=['POST', 'GET'])
#app.add_url_rule(rule='/init', view_func=init, methods=['POST'])
app.add_url_rule(rule='/test', view_func=hello.test_form, methods=['GET','POST'])


# websocket event
socketio.on_event('init', handler=init)
#socketio.on_event('connect', handler=)
socketio.on_event('message', handler=message)
socketio.on_event('json', handler=json_data)