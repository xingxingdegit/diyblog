import traceback
from flask import jsonify
from flask import request
from api import user
import logging
from flask import Flask, session, redirect, url_for, escape, request
from api import redis
import datetime
from api.logger import base_log
from api.init import create_user, create_table

log = logging.getLogger(__name__)


@base_log
def init():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    if username and password:
        create_table_state = create_table()
        if create_table_state:
            create_user_state = create_user(username, password)
            if create_user_state:
                return {'success': True, 'data': '数据表创建成功，用户创建成功'}
            else:
                return {'success': False, 'data': '用户创建失败'}
        else:
            return {'success': False, 'data': '数据库表创建失败'}

    else:
        return jsonify({'success': False, 'data': '信息不完整'})
    