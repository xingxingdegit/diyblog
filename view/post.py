from flask import render_template, g, make_response, request, jsonify
import logging
import traceback
from api.logger import base_log
from api.dbpool import with_db
from api.auth import backend_g_admin_url
from api.post import save_post
from api.post import check_something
from api.post import get_post_admin
from api.post import get_post_list

log = logging.getLogger(__name__)


@base_log
@backend_g_admin_url
def check_view():
    # check  title  and   url
    try:
        re_data = request.args
        title = re_data.get('title')
        url = re_data.get('url')
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
        page_num = int(data['page_num'])
        post_num_per_page = int(data['post_num_per_page'])
        return_data = get_post_list({'page_num': page_num, 'post_num_per_page': post_num_per_page})
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
        return_data = get_post_admin(use_data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
        pass
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})


@base_log
@backend_g_admin_url
def save_post_view():
    try:
        data = request.get_json()
        use_data = {}
        use_data['title'] = data['title'].strip()
        use_data['content'] = data['content']
        use_data['code_style'] = data['code_style'].strip()
        use_data['id'] = int(data.get('id', 0))
    
        return_data = save_post(use_data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})




