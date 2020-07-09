import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent / 'conf'))
import config
from route import route
# 加载一些初始化的模块
from api import logger
from api import dbpool


route.app.run(host=config.listen['host'], port=config.listen['port'], debug=config.DEBUG)




