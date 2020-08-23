from flask import g
from api.dbpool import select, with_db
import logging
import traceback

log = logging.getLogger(__name__)

@with_db('read')
def get_class_list(data=None):
    try:
        if data:
            pass
        else:
            data = g.db.select('class', fields=['id', 'classname', 'status', 'sort'], where={'status': [1, 2]})
            if data[0]:
                return True, data[1][1]
            else:
                return False, ''
    except Exception:
        log.error(traceback.format_exc())
    return False, ''
