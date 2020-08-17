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
app.add_url_rule(rule='/test/<path:other_url>/oooo', view_func=test_page, methods=['GET'])

from view.hello import test_form
from view.hello import hello
from view.hello import test_url
app.add_url_rule(rule='/test', view_func=test_form, methods=['POST'])
app.add_url_rule(rule='/hello', view_func=hello, methods=['GET'])
app.add_url_rule(rule='/hello/<path:admin_url>/test', view_func=test_url, methods=['GET'])


#####################################

# admin manager
from view.page import admin_login_page
from view.page import back_manage_page
from view.login import login
from view.login import get_key
from view.post import save_post_view
from view.post import check_view
from view.post import get_post_admin_view

# page
app.add_url_rule(rule='/admin/<path:admin_url>', view_func=admin_login_page, methods=['GET'])
app.add_url_rule(rule='/admin/<path:admin_url>/back_manage', view_func=back_manage_page, methods=['GET'])
# login api
app.add_url_rule(rule='/admin/<path:admin_url>/getkey', view_func=get_key, methods=['GET'])
app.add_url_rule(rule='/admin/<path:admin_url>/login', view_func=login, methods=['POST'])
# post api
app.add_url_rule(rule='/admin/<path:admin_url>/post/save', view_func=save_post_view, methods=['POST'])
app.add_url_rule(rule='/admin/<path:admin_url>/post/check', view_func=check_view, methods=['GET'])
app.add_url_rule(rule='/admin/<path:admin_url>/post/get', view_func=get_post_admin_view, methods=['POST'])
#####################################

# websocket event
from view.init import init
from view.init import init_check
socketio.on_event('init', handler=init)
socketio.on_event('init_check', handler=init_check)
#socketio.on_event('connect', handler=)
#socketio.on_event('message', handler=message)
#socketio.on_event('json', handler=json_data)