from flask import Flask
from view import hello
from view.login import login
from view.init import init
from config import secret_key
import logging

log = logging.getLogger(__name__)


app = Flask('diyblog')
app.secret_key = secret_key
app.debug = False


app.add_url_rule(rule='/hello', view_func=hello.hello, methods=['GET'])
app.add_url_rule(rule='/login', view_func=login, methods=['POST', 'GET'])
app.add_url_rule(rule='/init', view_func=init, methods=['POST'])
app.add_url_rule(rule='/test', view_func=hello.test_form, methods=['GET','POST'])


from flask_socketio import SocketIO
socketio = SocketIO(app)
socketio.server.eio.async_mode = 'eventlet'

def test_socket(data):
    log.info(data)

socketio.on_event('message', test_socket)
