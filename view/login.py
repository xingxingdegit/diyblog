import traceback
from flask import jsonify
from flask import request
from api import user
import logging
from flask import Flask, session, redirect, url_for, escape, request
import datetime
import random

log = logging.getLogger(__name__)


def login():
    if request.method == 'GET':
        data = user.get_key()
        if data[0]:
            log.info('{}:{}'.format('session', session))
            key = random.choice('abcdefghigklmnopqrstuvwxyz')
            session[key] = key

            return jsonify({'success': True, 'data': data[1]})
     
    elif request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            key = request.form.get('other', '').strip()
            if username and password and key:
                data = user.login(username, password, key)
                # 响应对象的设置也打算在这里设置。 还有cookie打算加密。
                if data[0]:
                    session['username'] = username
                    session['session_id'] = data[1]
            else:
                log.error('op:login|username:{}|password:{}|info:login information is Incomplete '.format(username, password))
                data = {'success': False, 'data': None}
            return jsonify(data)
        except Exception:
            log.error(traceback.format_exc())

