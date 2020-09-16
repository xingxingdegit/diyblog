import traceback
from flask import jsonify
from flask import request
from api import user
from flask import Flask, session, redirect, url_for, escape, request, g, make_response
import datetime
import random
import logging
from api.logger import base_log
from api.auth import backend_g_admin_url
from api.user import change_passwd
from api.user import logout

log = logging.getLogger(__name__)

@base_log
@backend_g_admin_url
def get_key():
    if request.method == 'GET':
        data = user.get_key()
        if data[0]:
            return jsonify({'success': True, 'data': data[1]})
        else:
            return jsonify({'success': False, 'data': data[1]})

     
@base_log
@backend_g_admin_url
def login_view():
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
                response.set_cookie('session', session)
                response.set_cookie('username', username)
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


@base_log
@backend_g_admin_url
def change_passwd_view():
    try:
        cookies = request.cookies
        username = cookies['username'].strip()
        data = request.get_json()
        return_data = change_passwd(data, username)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})


@base_log
@backend_g_admin_url
def logout_view():
    try:
        data = request.get_json()
        username = data['username'].strip()
        username2 = request.cookies['username'].strip()
        if username == username2:
            return_data = logout(username)
            if return_data[0]:
                return jsonify({'success': True, 'data': return_data[1]})
            else:
                return jsonify({'success': False, 'data': return_data[1]})

    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})