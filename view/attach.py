from flask import render_template, g, make_response, request, jsonify
import logging
import traceback
from api.logger import base_log
from api.attach import get_attach_list
from api.attach import get_mini_photo

log = logging.getLogger(__name__)


@base_log
def get_attach_list_view():
    pass


@base_log
def get_mini_photo_view():
    try:
        re_data = request.args
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

