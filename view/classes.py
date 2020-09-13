from flask import request, jsonify
from api.auth import backend_g_admin_url
import logging
import traceback
from api.logger import base_log
from api.classes import get_class_list
from api.classes import get_tags_list
from api.classes import add_class
from api.classes import add_tag
from api.classes import del_class
from api.classes import del_tag
from api.classes import check_classname
from api.classes import check_tagname

log = logging.getLogger(__name__)


@base_log
@backend_g_admin_url
def check_classname_view():
    try:
        re_data = request.args
        class_name = re_data.get('class_name', '').strip()
        return_data = check_classname(class_name)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def check_tagname_view():
    try:
        re_data = request.args
        tag_name = re_data.get('tag_name', '').strip()
        return_data = check_tagname(tag_name)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})


@base_log
def get_class_list_view():
    try:
        args = request.args
        if args:
            return_data = get_class_list(args)
        else:
            return_data = get_class_list()
    
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})


@base_log
def get_tags_list_view():
    try:
        args = request.args
        return_data = get_tags_list(args)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})


@base_log
@backend_g_admin_url
def add_class_view():
    try:
        data = request.get_json()
        return_data = add_class(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def add_tag_view():
    try:
        data = request.get_json()
        return_data = add_tag(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})


@base_log
@backend_g_admin_url
def del_class_view():
    try:
        data = request.get_json()
        return_data = del_class(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})

@base_log
@backend_g_admin_url
def del_tag_view():
    try:
        data = request.get_json()
        return_data = del_tag(data)
        if return_data[0]:
            return jsonify({'success': True, 'data': return_data[1]})
        else:
            return jsonify({'success': False, 'data': return_data[1]})
    except Exception:
        log.error(traceback.format_exc())
    return jsonify({'success': False, 'data': ''})
