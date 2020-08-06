from flask import render_template, g, make_response
import logging
import traceback
from api.logger import base_log
from api.dbpool import with_db
from api.auth import admin_url_auth_wrapper, auth_mode, wrapper_page_login

log = logging.getLogger(__name__)

# 主页
def home_page():
    return render_template('index.html')


# 文章页
def post_page(post_url):
    return render_template('post.html')

# 初始化
def init_page():
    return render_template('init.html')

# 测试页
def test_page(other_url):
    log.info('1111111111')
    log.info('11111111111,other_url: {}'.format(other_url))
    return other_url, 200


# 后台登录
@base_log
@admin_url_auth_wrapper('page')
def admin_login_page():
    return render_template('login.html')

@base_log
@admin_url_auth_wrapper('page')
@wrapper_page_login
@auth_mode('login')
def back_manage_page():
    return render_template('back.html')