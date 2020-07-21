import traceback
from flask import jsonify
from flask import request
from api import user
from flask import Flask, session, redirect, url_for, escape, request, g, make_response
import datetime
import random
import logging
from api.logger import base_log
from api.auth import admin_url_auth, admin_url_auth_wrapper

log = logging.getLogger(__name__)

@base_log
@admin_url_auth_wrapper
def get_key():
    if request.method == 'GET':
        data = user.get_key()
        if data[0]:
            return jsonify({'success': True, 'data': data[1]})
     
@admin_url_auth_wrapper
def login():
    return_data = {'success': False, 'data': None}
    try:
        userdata = request.get_json()
        username = userdata.get('username', '').strip()
        password = userdata.get('password', '').strip()
        key = userdata.get('other', '').strip()
        if username and password and key:
            data = user.login(username, password, key)
            # 响应对象的设置也打算在这里设置。 还有cookie打算加密。
            if data[0]:
                session = data[1]
                return_data = {'success': True, 'data': None}
                response = make_response(return_data)
                response.set_cookie('sessionId', session)
                response.status_code = 200
                return response
            else:
                if data[1]:
                    return_data['data'] = data[1]
                    response = make_response(return_data)
                    return response
        else:
            log.error('func:login|username:{}|password:***|info:login information is Incomplete '.format(username))
    except Exception:
        log.error(traceback.format_exc())
    return jsonify(return_data)

