from flask import request, jsonify
import logging
import traceback
from api.logger import base_log
from api.auth import backend_g_admin_url
from api.upload import upload_file

log = logging.getLogger(__name__)


@base_log
@backend_g_admin_url
def upload_file_view():
    try:
        files = request.files
        other_data = request.form
        headers = request.headers
        file_size = int(headers.get('Content-Length', 0))
        return_data = upload_file(files, file_size, other_data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})


