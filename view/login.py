import traceback
from flask import jsonify
from flask import request
from api import user
import logging
import redis

log = logging.getLogger(__name__)


def login():
    if request.method == 'GET':
        data = user.get_key()
        if data[0]:
            return jsonify({'success': True, 'data': data})
     
    elif request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            key = request.form.get('other')
            if username and password and key:
                data = user.login(username, password, key)
                # 响应对象的设置也打算在这里设置。 还有cookie打算加密。
                if data == True:
                    data = {
                        'success': True,
                        'data': data
                    }
            else:
                data = {'success': False, 'data': None}
            return jsonify(data)
        except Exception:
            pass

