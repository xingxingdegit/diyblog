from flask import render_template, g, make_response
import logging
import traceback
from api.logger import base_log
from api.dbpool import with_db

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
    return render_template('404.html'), 200


# 后台登录
@base_log
@with_db('read')
def admin_login_url(admin_login_url):
    try:
        setting = g.db.select('setting', fields=['value'], where={'key': 'admin_login_url'})
        if setting[0]:
            if setting[1][0]:
                if admin_login_url == setting[1][1][0]['value']:
                    return render_template('login.html')
    except Exception:
        log.error(traceback.format_exc())
    return render_template('404.html'), 404

