from api.dbpool import with_db, select, with_redis
from api.auth import admin_url_auth_wrapper, auth_mode, cors_auth
from flask import g
import logging
import traceback
import datetime

log = logging.getLogger(__name__)

def get_mini_photo(data):
    pass