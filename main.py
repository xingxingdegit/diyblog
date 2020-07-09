import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent / 'conf'))
from base import logger
import logging
import config
from route import route
from base import dbpool
print(sys.path)


log = logging.getLogger(__name__)

route.app.run(host=config.listen['host'], port=config.listen['port'], debug=config.DEBUG)




