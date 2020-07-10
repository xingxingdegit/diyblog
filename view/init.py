import traceback
from flask import jsonify
from flask import request
from api import user
import logging
from flask import Flask, session, redirect, url_for, escape, request
import datetime
from api.logger import base_log
from api.init import create_user, create_table
from flask_socketio import SocketIO, send, emit

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
