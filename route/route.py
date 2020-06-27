from flask import Flask
from view import hello
from api import user
from config import secret_key


app = Flask('myiterm')
app.secret_key = secret_key


app.add_url_rule(rule='/hello', view_func=hello.hello, methods=['GET'])
app.add_url_rule(rule='/login', view_func=user.login, methods=['POST'])
#app.add_url_rule('/weixin', view_func=weixin.WxParse, methods=['GET', 'POST'])
#app.add_url_rule('/login', view_func=user.Login, methods=['POST'])
#app.add_url_rule('/logout', view_func=user.Logout, methods=['GET'])
