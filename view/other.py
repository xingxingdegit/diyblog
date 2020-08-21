from flask import request, jsonify
import logging
import traceback
from api.logger import base_log
from api.auth import backend_g_admin_url
from api.other import get_url

log = logging.getLogger(__name__)

@base_log
@backend_g_admin_url
def get_url_view():
    try:
        re_data = request.args
        rtype = re_data['type'].strip()
        return_data = get_url(rtype)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})