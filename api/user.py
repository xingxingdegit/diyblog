from flask import request, session
import logging
from flask import jsonify

log = logging.getLogger(__name__)

def login():
    user = request.form['user']
    password = request.form['password']
    log.info('user: {}|password: {}'.format(user, password))
    session['username'] = user
    session['password'] = password
    return jsonify([user, password])


