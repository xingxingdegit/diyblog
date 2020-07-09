import traceback
from flask import jsonify
from flask import request
from base import dbpool
from api import user
import logging
from flask import Flask, session, redirect, url_for, escape, request
from base import redis
import datetime

log = logging.getLogger(__name__)


def init():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    if username and password:
        create_table = 
        data = user.create_user(username, password)
    else:
        return jsonify({'success': False, 'data': '信息不完整'})
    