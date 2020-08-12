from flask import render_template, g, make_response, request, jsonify
import logging
import traceback
from api.logger import base_log
from api.dbpool import with_db
from api.auth import backend_g_admin_url
from api.post import save_post

log = logging.getLogger(__name__)


@base_log
@backend_g_admin_url
def check_title():
    data = request.get_json()
    pass

@base_log
@backend_g_admin_url
def save_post_view():
    try:
        data = request.get_json()
        use_data = {}
        use_data['title'] = data['title'].strip()
        use_data['content'] = data['content']
        use_data['id'] = int(data.get('id', 0))
    
        return_data = save_post(use_data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})




