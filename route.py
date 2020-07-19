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
from view.page import home_page
from view.page import post_content

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
# page
app.add_url_rule(rule='/', view_func=home_page, methods=['GET'])
app.add_url_rule(rule='/page/<post_url>', view_func=post_page, methods=['GET'])

# post
app.add_url_rule(rule='/post/<post_url>', view_func=post_content, methods=['GET'])

# back_manager


# websocket event
socketio.on_event('init', handler=init)
#socketio.on_event('connect', handler=)
socketio.on_event('message', handler=message)
socketio.on_event('json', handler=json_data)