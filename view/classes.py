from flask import request, jsonify
import logging
import traceback
from api.logger import base_log
from api.classes import get_class_list

log = logging.getLogger(__name__)


@base_log
def get_class_list_view():
    try:
        args = request.args
        if args:
            pass
        else:
            return_data = get_class_list()
    
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})