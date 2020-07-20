from flask import Flask
from flask_socketio import SocketIO, send, emit
import logging

##########################################################

log = logging.getLogger(__name__)
app = Flask('diyblog')
app.debug = False
socketio = SocketIO(app)
socketio.server.eio.async_mode = 'eventlet'

##########################################################

# api

#####################################

# page
from view.page import home_page
from view.page import post_page
from view.page import init_page
app.add_url_rule(rule='/', view_func=home_page, methods=['GET'])
app.add_url_rule(rule='/page/post/<post_url>', view_func=post_page, methods=['GET'])
app.add_url_rule(rule='/page/init', view_func=init_page, methods=['GET'])

#####################################

# test page
from view.page import test_page
app.add_url_rule(rule='/test/<path:other_url>', view_func=test_page, methods=['GET'])

from view.hello import test_form
app.add_url_rule(rule='/test', view_func=test_form, methods=['POST'])

#####################################

# admin manager
from view.page import admin_login_url
from view.login import login
from view.login import get_key
app.add_url_rule(rule='/admin/<path:admin_login_url>', view_func=admin_login_url, methods=['GET'])
app.add_url_rule(rule='/login/getkey', view_func=get_key, methods=['GET'])
app.add_url_rule(rule='/login/login', view_func=login, methods=['POST'])
#####################################

# websocket event
from view.init import init
socketio.on_event('init', handler=init)
#socketio.on_event('connect', handler=)
#socketio.on_event('message', handler=message)
#socketio.on_event('json', handler=json_data)