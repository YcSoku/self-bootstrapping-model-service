import os
import atexit
import logging
from flask import Blueprint

from . import config
from . import registry
from .app import create_app
from .util import StorageMonitor
from .model import launcher, Dispatcher, monitoring

def initialize_work_space():
    
    if config.APP_DEBUG:
        util.delete_folder_contents(config.DIR_MODEL_CASE)

    if not os.path.exists(config.DIR_MODEL_CASE):
        os.makedirs(config.DIR_MODEL_CASE)
        
    for key in registry.get_registry():
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

def run(name: str = None, bps: list[Blueprint] = None, template_folder: str = None, static_folder: str = None, static_url_path: str = None):
    
    initialize_work_space()

    app = create_app(
        name,
        bps,
        template_folder,
        static_folder,
        static_url_path
    )
    
    app.run(host = "0.0.0.0", port = config.APP_PORT, debug = config.APP_DEBUG)
    

if __name__ == '__main__':
    
    run()
