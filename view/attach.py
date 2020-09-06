from flask import render_template, request, jsonify, send_file
import logging
import traceback
from api.auth import backend_g_admin_url
from api.logger import base_log
from api.attach import get_attach_list
from api.attach import get_mini_photo
from api.attach import get_mimetype_list
from api.attach import get_private_file

log = logging.getLogger(__name__)

@base_log
def get_private_file_view(private_file):
    try:
        private_file = private_file.strip()
        if '/' not in private_file:
            if '\\' not in private_file:
                state = get_private_file(private_file)
                if state[0]:
                    return send_file(state[1])

    except Exception:
        log.error(traceback.format_exc())
    return render_template('404.html'), 404

@base_log
@backend_g_admin_url
def get_mimetype_list_view():
    try:
        return_data = get_mimetype_list()
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def get_attach_list_view():
    try:
        data = request.get_json()
        return_data = get_attach_list(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})


@base_log
@backend_g_admin_url
def get_mini_photo_view():
    try:
        re_data = request.get_json()
        filename = re_data.get('filename', '').strip()
        size_level = int(re_data.get('size_level', 1))

        return_data = get_mini_photo({'filename': filename, 'size_level': size_level})
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

