from flask import Flask
from view import hello
from view.login import login
from view.init import init
from config import secret_key


app = Flask('diyblog')
app.secret_key = secret_key


app.add_url_rule(rule='/hello', view_func=hello.hello, methods=['GET'])
app.add_url_rule(rule='/login', view_func=login, methods=['POST', 'GET'])
app.add_url_rule(rule='/init', view_func=init, methods=['POST'])
app.add_url_rule(rule='/test', view_func=hello.test_form, methods=['GET','POST'])