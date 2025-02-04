import os
import atexit
import config
import logging
from app import create_app
from util import StorageMonitor
from model import launcher, Dispatcher, monitoring

def initialize_work_space():

    if not os.path.exists(config.DIR_MODEL_CASE):
        os.makedirs(config.DIR_MODEL_CASE)
        
    for key in config.MODEL_REGISTRY:
        launcher.preheat(key)
         
    StorageMonitor().initialize([config.DIR_ROOT], config.DIR_STORAGE_LOG)
    Dispatcher().initialize(monitoring)
    
@atexit.register
def on_exit():
    
    Dispatcher.exit()

werkzeug_logger = logging.getLogger('werkzeug')

class Filter200(logging.Filter):
    def filter(self, record):
        return " 200 " not in record.getMessage()

werkzeug_logger.addFilter(Filter200())
    

if __name__ == '__main__':
    
    initialize_work_space()

    app = create_app()
    
    app.run(host = "0.0.0.0", port = config.APP_PORT, debug = config.APP_DEBUG)
