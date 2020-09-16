from flask import request, jsonify
from api.auth import backend_g_admin_url
import logging
import traceback
from api.logger import base_log
from api.notice import get_static_notice
from api.notice import set_static_notice

log = logging.getLogger(__name__)



@base_log
@backend_g_admin_url
def get_static_notice_view():
    try:
        return_data = get_static_notice()
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})



@base_log
@backend_g_admin_url
def set_static_notice_view():
    try:
        data = request.get_json()
        return_data = set_static_notice(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})