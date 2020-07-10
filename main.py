import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent / 'conf'))
from config import listen
# 加载一些初始化的模块
from api import logger
from api import dbpool
#
from gevent.pywsgi import WSGIServer
from route import app

''' 
python version: 3.8.2
'''


http_server = WSGIServer((listen['host'], listen['port']), app)
http_server.serve_forever()


#app.run(host=config.listen['host'], port=config.listen['port'])




