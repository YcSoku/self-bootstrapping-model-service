import os
import sys
import types
import webbrowser
from pathlib import Path
from threading import Thread
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from . import config
from . import registry
from .app import base_router 
from .util import StorageMonitor
from .model import launcher, Dispatcher, monitoring

open_browser_when_creation = False
origins = [
    f'http://localhost:{config.APP_PORT}'
]

def init(
    name: str = None, 
    routers: list[APIRouter] = None, 
    template_folder: str = None, 
    static_folder: str = None, 
    static_url_path: str = None,
    open_browser: bool = False):

    # Local helpers ##################################################
    
    def get_uvicorn_path(self):
        for name, module in sys.modules.items():
            if hasattr(module, "__dict__"):
                for attr_name, attr_value in module.__dict__.items():
                    if attr_value is self:
                        return f"{name}:{attr_name}"
        raise RuntimeError('Unable to find full path to FastAPI instance')
    
    # Init operations ##################################################
    
    global open_browser_when_creation
    
    app = FastAPI(title=name or 'SBMS APP', lifespan=lifespan)
    app.include_router(base_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.get_uvicorn_path = types.MethodType(get_uvicorn_path, app)
    
    if static_folder:
        static_folder_path = Path(static_folder).resolve()
        if static_folder_path.exists():
            app.mount(static_url_path, StaticFiles(directory=str(static_folder_path)), name="static")
            
    templates = Jinja2Templates(directory=template_folder) if template_folder else None
    
    if routers:
        for router in routers:
            app.include_router(router)
    
    if open_browser:
        open_browser_when_creation = open_browser
    
    return app

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    if config.APP_DEBUG and os.path.exists(config.DIR_MODEL_CASE):
        util.delete_folder_contents(config.DIR_MODEL_CASE)

    if not os.path.exists(config.DIR_MODEL_CASE):
        os.makedirs(config.DIR_MODEL_CASE)
        
    for key in registry.get_registry():
        launcher.preheat(key)
         
    StorageMonitor().initialize([config.DIR_ROOT], config.DIR_STORAGE_LOG)
    Dispatcher().initialize(monitoring)
    
    if open_browser_when_creation:
        def open_url():
            import time
            time.sleep(1)
            webbrowser.open(f"http://127.0.0.1:{config.APP_PORT}{config.API_DOCS}")
            
        Thread(target=open_url, daemon=True).start()
        
    yield
    
    Dispatcher().destroy()
    StorageMonitor().destroy()
