import traceback
from flask import jsonify
from flask import request
from api import user
import logging
from flask import Flask, session, redirect, url_for, escape, request
import datetime
import json
from api.logger import base_log
from api.init import create_user, create_table, init_setting
from flask_socketio import SocketIO, send, emit
import os
import base64

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
def init(data):
    emit('init', {'stage': 'start', 'data': 'begin...'})
    sitename = data.get('sitename', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    beginning = {'stage': 'in', 'data': {}}
    beginning['data'].update({'tag': 'check_user', 'type': 'key', 'data': '用户信息检查', 'state': None})
    emit('init', beginning, callback=False)
    if username and password and sitename:
        beginning['data'].update({'tag': 'check_user', 'type': 'value', 'data': '成功', 'state': 'success'})
        emit('init', beginning)

        beginning['data'].update({'tag': 'create_table', 'type': 'key', 'data': '创建数据表', 'state': None})
        emit('init', beginning)
        create_table_state = create_table()
        if create_table_state:
            beginning['data'].update({'tag': 'create_table', 'type': 'value', 'data': '成功', 'state': 'success'})
            emit('init', beginning)

            # 用户加密cookie的秘钥，cookie里存放用户名与sessioinID, 没有密码相关信息.
            beginning['data'].update({'tag': 'user_key', 'type': 'key', 'data': '创建用户秘钥', 'state': None})
            emit('init', beginning)
            cookie_key = base64.b64encode(os.urandom(21)).decode('utf-8')
            if cookie_key:
                beginning['data'].update({'tag': 'user_key', 'type': 'value', 'data': '成功', 'state': 'success'})
                emit('init', beginning)
            else:
                beginning['data'].update({'tag': 'user_key', 'type': 'value', 'data': '失败', 'state': 'fail'})
                emit('init', beginning)
                emit('init', {'stage': 'end', 'data': 'end'})
                return False

            beginning['data'].update({'tag': 'create_user', 'type': 'key', 'data': '创建用户', 'state': None})
            emit('init', beginning)
            data['cookie_key'] = cookie_key
            create_user_state = create_user(data)
            if create_user_state:
                beginning['data'].update({'tag': 'create_user', 'type': 'value', 'data': '成功', 'state': 'success'})
                emit('init', beginning)
            else:
                beginning['data'].update({'tag': 'create_user', 'type': 'value', 'data': '失败', 'state': 'fail'})
                emit('init', beginning)
                emit('init', {'stage': 'end', 'data': 'end'})
                return False
            beginning['data'].update({'tag': 'init_setting', 'type': 'key', 'data': '添加默认设置', 'state': None})
            emit('init', beginning)
            init_setting_state = init_setting(data)
            if init_setting_state:
                beginning['data'].update({'tag': 'init_setting', 'type': 'value', 'data': '成功', 'state': 'success'})
                emit('init', beginning)
            else:
                beginning['data'].update({'tag': 'init_setting', 'type': 'value', 'data': '失败', 'state': 'fail'})
                emit('init', beginning)
        else:
            beginning['data'].update({'tag': 'create_table', 'type': 'value', 'data': '失败', 'state': 'fail'})
            emit('init', beginning)
    else:
        beginning['data'].update({'tag': 'check_user', 'type': 'value', 'data': '失败', 'state': 'fail'})
        emit('init', beginning)
    emit('init', {'stage': 'end', 'data': 'end'})


    
def test_socket(data):
    print('test_socket: {}'.format(data))
    log.info(data)
    log.info('11111111111')
    return '1111111'
  
def test_socket1():
    print('test_socket: {}'.format('2222222'))
    log.info('222222222')
    return '22222222'

def message(data1):
    log.info('data1:{}'.format(data1))
    send(data1)

def json_data(data):
    log.info('json: {}'.format(data))
