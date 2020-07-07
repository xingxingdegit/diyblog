import traceback
from flask import jsonify
from flask import request
import logging

log = logging.getLogger(__name__)

def hello():
    return 'hello world'


def test_form():
    try:
        path = request.path
        full_path = request.full_path
        url = request.url
        base_url = request.base_url
        url_root = request.url_root
        form = request.form
        args = request.args
        files = request.files
    #    print('form: {}'.format(type(form)))
    #    print('args: {}'.format(type(args)))
    #    print('files: {}'.format(type(files)))
    #    print('files: {}'.format(files))
        files1_storage = files['file1']
        print(files1_storage.stream.read())
    #    with open('333.txt', 'wb') as fd:
    #        files1_storage.save(fd)
    
    #    files1_storage.stream.seek(0)
    #    files1_storage.save('123.txt')
    
    #    file_storage_help = dir(files1_storage)
    #    stream = files1_storage.stream
    #   stream_help = dir(stream)
    except Exception:
        log.error(traceback.format_exc())

    try:
        print(type(form['test.x']))
        print(form['test.x'])
    except Exception as e:
        log.error(traceback.format_exc())

    response_data = [
        {'args': args},
        {'form': form},
        {'path': path}, 
        {'full_path': full_path},
        {'url': url},
        {'base_url': base_url},
        {'url_root': url_root},
    ]
#    for one in files:
#        name = one
#        data = files[one]
#        response_data.append()

    return jsonify(response_data)

