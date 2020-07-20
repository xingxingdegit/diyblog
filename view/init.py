from flask import Flask, session, redirect, url_for, escape, request, jsonify
from flask_socketio import SocketIO, send, emit
from cryptography.fernet import Fernet
import traceback
import logging
import os
import datetime
import json
#
from api.logger import base_log
from api.init import create_user, create_table, init_setting
from api import user
from api.auth import auth_mode

log = logging.getLogger(__name__)


#@base_log
#def init():
#    username = request.form.get('username', '').strip()
#    password = request.form.get('password', '').strip()
#    if username and password:
#        create_table_state = create_table()
#        if create_table_state:
#            create_user_state = create_user(username, password)
#            if create_user_state:
#                return {'success': True, 'data': '数据表创建成功，用户创建成功'}
#            else:
#                return {'success': False, 'data': '用户创建失败'}
#        else:
#            return {'success': False, 'data': '数据库表创建失败'}
#
#    else:
#        return jsonify({'success': False, 'data': '信息不完整'})

@base_log
@auth_mode('init')
def init(data):
    emit('init', {'stage': 'start', 'data': 'begin...'})
    sitename = data.get('sitename', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    state = False

    beginning = {'stage': 'in', 'data': {}}
    beginning['data'].update({'tag': 'check_user', 'type': 'key', 'data': '用户信息检查', 'state': None, 'progress': 5})
    emit('init', beginning, callback=False)
    if username and password and sitename:
        beginning['data'].update({'tag': 'check_user', 'type': 'value', 'data': '成功', 'state': 'success', 'progress': 20})
        emit('init', beginning)

        beginning['data'].update({'tag': 'create_table', 'type': 'key', 'data': '创建数据表', 'state': None, 'progress': 25})
        emit('init', beginning)
        create_table_state = create_table()
        if create_table_state:
            beginning['data'].update({'tag': 'create_table', 'type': 'value', 'data': '成功', 'state': 'success', 'progress': 40})
            emit('init', beginning)

            # 用户加密cookie的秘钥，cookie里存放用户名与sessioinID, 没有密码相关信息.
            beginning['data'].update({'tag': 'user_key', 'type': 'key', 'data': '创建用户秘钥', 'state': None, 'progress': 45})
            emit('init', beginning)
            cookie_key = Fernet.generate_key().decode()
            if cookie_key:
                beginning['data'].update({'tag': 'user_key', 'type': 'value', 'data': '成功', 'state': 'success', 'progress': 60})
                emit('init', beginning)
            else:
                beginning['data'].update({'tag': 'user_key', 'type': 'value', 'data': '失败', 'state': 'fail', 'progress': 45})
                emit('init', beginning)
                emit('init', {'stage': 'end', 'data': 'end'})
                return False

            beginning['data'].update({'tag': 'create_user', 'type': 'key', 'data': '创建用户', 'state': None, 'progress': 65})
            emit('init', beginning)
            data['cookie_key'] = cookie_key
            create_user_state = create_user(data)
            if create_user_state:
                beginning['data'].update({'tag': 'create_user', 'type': 'value', 'data': '成功', 'state': 'success', 'progress': 80})
                emit('init', beginning)
            else:
                beginning['data'].update({'tag': 'create_user', 'type': 'value', 'data': '失败', 'state': 'fail', 'progress': 65})
                emit('init', beginning)
                emit('init', {'stage': 'end', 'data': 'end'})
                return False
            beginning['data'].update({'tag': 'init_setting', 'type': 'key', 'data': '添加默认设置', 'state': None, 'progress': 85})
            emit('init', beginning)
            init_setting_state = init_setting(data)
            if init_setting_state:
                beginning['data'].update({'tag': 'init_setting', 'type': 'value', 'data': '成功', 'state': 'success', 'progress': 100})
                emit('init', beginning)
                state = True
            else:
                beginning['data'].update({'tag': 'init_setting', 'type': 'value', 'data': '失败', 'state': 'fail', 'progress': 85})
                emit('init', beginning)
        else:
            beginning['data'].update({'tag': 'create_table', 'type': 'value', 'data': '失败', 'state': 'fail', 'progress': 25})
            emit('init', beginning)
    else:
        beginning['data'].update({'tag': 'check_user', 'type': 'value', 'data': '失败', 'state': 'fail', 'progress': 5})
        emit('init', beginning)
    emit('init', {'stage': 'end', 'data': 'end', 'state': state})
