from flask import Flask
from view import hello
from view.login import login
from config import secret_key


app = Flask('diyblog')
app.secret_key = secret_key


app.add_url_rule(rule='/hello', view_func=hello.hello, methods=['GET'])
app.add_url_rule(rule='/login', view_func=login, methods=['POST', 'GET'])
app.add_url_rule(rule='/init', view_func=login, methods=['POST', 'GET'])
app.add_url_rule(rule='/test', view_func=hello.test_form, methods=['GET','POST'])
#app.add_url_rule('/weixin', view_func=weixin.WxParse, methods=['GET', 'POST'])
#app.add_url_rule('/login', view_func=user.Login, methods=['POST'])
#app.add_url_rule('/logout', view_func=user.Logout, methods=['GET'])
