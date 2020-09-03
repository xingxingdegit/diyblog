from flask import render_template, g, make_response, request, jsonify
import logging
import traceback
from api.logger import base_log
from api.auth import backend_g_admin_url
from api.post import save_post
from api.post import check_something
from api.post import get_post_admin
from api.post import get_post_list
from api.post import remove_post
from api.post import cancel_remove
from api.post import del_post
from api.post import publish_post
from api.post import publish_post_state
from api.post import publish_cancel

log = logging.getLogger(__name__)


@base_log
@backend_g_admin_url
def check_view():
    # check  title  and   url
    try:
        re_data = request.args
        title = re_data.get('post_title', '').strip()
        url = re_data.get('post_url', '').strip()
        return_data = check_something({'title': title, 'url': url})
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def get_post_list_view():
    try:
        data = request.get_json()
        return_data = get_post_list(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def get_post_admin_view():
    try:
        data = request.get_json()
        use_data = {}
        use_data['id'] = int(data.get('id', 0))
        use_data['filter'] = data.get('filter', '').strip()
        return_data = get_post_admin(use_data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def remove_post_view():
    try:
        data = request.get_json()
        return_data = remove_post(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def cancel_remove_view():
    try:
        data = request.get_json()
        return_data = cancel_remove(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def del_post_view():
    try:
        data = request.get_json()
        return_data = del_post(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def save_post_view():
    try:
        data = request.get_json()
        use_data = {}
        use_data['title'] = data['post_title'].strip()
        use_data['content'] = data['post_content']
        use_data['code_style'] = data['code_style'].strip()
        use_data['id'] = int(data.get('post_id', 0))
    
        return_data = save_post(use_data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def publish_post_view():
    try:
        data = request.get_json()
        return_data = publish_post(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def publish_post_state_view():
    try:
        data = request.get_json()
        return_data = publish_post_state(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def publish_cancel_view():
    try:
        data = request.get_json()
        return_data = publish_cancel(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

