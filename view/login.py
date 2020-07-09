import traceback
from flask import jsonify
from flask import request
from api import user
from flask import Flask, session, redirect, url_for, escape, request, g
import datetime
import random
import logging
from api.logger import base_log

log = logging.getLogger(__name__)


@base_log
def login():
    if request.method == 'GET':
        data = user.get_key()
        if data[0]:
            g.name = 'star'
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
                log.error('func:login|username:{}|password:***|info:login information is Incomplete '.format(username))
                data = {'success': False, 'data': None}
            return jsonify(data)
        except Exception:
            log.error(traceback.format_exc())

