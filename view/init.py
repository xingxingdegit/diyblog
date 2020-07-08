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
    username = request.form.get('username')
    password = request.form.get('password')
