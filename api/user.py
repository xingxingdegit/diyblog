import logging
import random


log = logging.getLogger(__name__)

def login():
    user = request.form['user']
    password = request.form['password']
    log.info('user: {}|password: {}'.format(user, password))
    session['username'] = user
    session['password'] = password
    return jsonify([user, password])


def get_key():
    key = [0] * 30
    for i in range(30):
        key[i] = random.randrange(128)
    return True, bytes(key).decode('utf-8')

