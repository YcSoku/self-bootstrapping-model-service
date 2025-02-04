import os
import sys
import util
import json
import types
import config
import marshal
import traceback
import functools
import py_compile
from .dispatcher import Dispatcher
from .modelCaseReference import ModelCaseReference as MCR

######################################## AOP ########################################

def model_status_controller_sync(func):
    
    @functools.wraps(func)
    def wrapper(mcr: MCR, *args, **kwargs):
        
        # Return if mcr is unlocked (COMPLETE or ERROR)
        if mcr.find_status(config.STATUS_COMPLETE) or mcr.find_status(config.STATUS_ERROR):
            return
        
        # Run
        try:
            mcr.update_status(config.STATUS_LOCK | config.STATUS_RUNNING)
                
            result = func(mcr, *args, **kwargs)
            
            mcr.make_response(result)
            mcr.update_status(config.STATUS_UNLOCK | config.STATUS_COMPLETE)
            util.update_size(config.DIR_STORAGE_LOG, util.get_folder_size_in_gb(mcr.directory))
            return
        
        except Exception as e:
            
            mcr.update_status(config.STATUS_UNLOCK | config.STATUS_ERROR, e, 'w')
            util.update_size(config.DIR_STORAGE_LOG, util.get_folder_size_in_gb(mcr.directory))
            traceback.print_exc()
            return
        
    return wrapper

######################################## Utils ########################################

def get_pyc_filename(script_name: str):
    
    python_version = f"{sys.version_info.major}{sys.version_info.minor}"
    
    pyc_filename = f"{script_name}.cpython-{python_version}.pyc"
    return pyc_filename

def load_code_from_pyc(pyc_path: str):
    with open(pyc_path, 'rb') as f:
        f.read(16)  # Skip the .pyc header (timestamp, magic number, etc.)
        code_obj = marshal.load(f)
    return code_obj

def compile_model_script_to_pyc(model_api: str, script_path: str):
    
    code_md5 = util.generate_md5(model_api)
    pyc_filename = get_pyc_filename(code_md5)
    compiled_path = os.path.join(config.DIR_RESOURCE_MODEL, code_md5)
    pyc_file_path = os.path.join(compiled_path, pyc_filename)
    
    script_modified_time = os.path.getmtime(script_path)
    
    if os.path.exists(compiled_path):
        try:
            
            with open(os.path.join(compiled_path, 'time.txt'), 'r', encoding='utf-8') as file:
                program_modified_time = float(file.readline())
                
            existing_pyc_files = [f for f in os.listdir(compiled_path) if f.endswith('.pyc')]
            if existing_pyc_files:
                
                existing_version = existing_pyc_files[0].split('.')[-2].replace('cpython-', '')
                current_version = f"{sys.version_info.major}{sys.version_info.minor}"
                
                if existing_version != current_version or program_modified_time != script_modified_time:
                    
                    for old_pyc in existing_pyc_files:
                        os.remove(os.path.join(compiled_path, old_pyc))
                else:
                    
                    return
        except FileNotFoundError:
            pass
    
    if not os.path.exists(compiled_path):
        os.makedirs(compiled_path)
    
    with open(os.path.join(compiled_path, 'time.txt'), 'w', encoding='utf-8') as file:
        file.write(str(script_modified_time))
        
    py_compile.compile(script_path, cfile=pyc_file_path)
    print(f"Model Program ({os.path.basename(script_path)}) Is Compiled to .pyc", flush=True)

######################################## Model Launcher ########################################

class ModelLauncher:
    
    def __init__(self, api: str):
        
        self.api = api
        self.lock = None
        self.id = util.generate_md5(api)
        self.script_path = os.path.join(config.DIR_RESOURCE_MODEL_TRIGGER, config.MODEL_REGISTRY[api])
        self.program_path = os.path.join(config.DIR_RESOURCE_MODEL, self.id, get_pyc_filename(self.id))
        
        code_obj = load_code_from_pyc(self.program_path)
        
        local_namespace = {}
        exec(code_obj, local_namespace, local_namespace)
        
        self.name = local_namespace['NAME'] if 'NAME' in local_namespace else 'Unknown Name'
        self.category = local_namespace['CATEGORY'] if 'CATEGORY' in local_namespace else 'Unknown Category'
        self.category_alias = local_namespace['CATEGORY_ALIAS'] if 'CATEGORY_ALIAS' in local_namespace else 'Unknown Category Alias'
        
        self.fire = types.MethodType(local_namespace['RUNNING'], self) if 'RUNNING' in local_namespace else lambda: None
        self.parse = types.MethodType(local_namespace['PARSING'], self) if 'PARSING' in local_namespace else lambda: None
        self.response = types.MethodType(local_namespace['RESPONSING'], self) if 'RESPONSING' in local_namespace else lambda: None
        
    @staticmethod
    def preheat(api: str):
        
        script_path = os.path.join(config.DIR_RESOURCE_MODEL_TRIGGER, config.MODEL_REGISTRY[api])
        compile_model_script_to_pyc(api, script_path)

    def dispatch(self, request_json: dict, other_dependent_ids: list[str] = []) -> MCR:
        
        other_pre_mcrs = [self.connect_model_case(id) for id in other_dependent_ids]
        default_pre_mcrs = self.parse(request_json, other_dependent_ids)
        mcrs = other_pre_mcrs + default_pre_mcrs
        
        # Check whether core model case is valid for running
        if self.check_(mcrs):
            
            # Dispatch model
            command = [self.api] + [mcr.id for mcr in mcrs]
            Dispatcher().dispatch(command)
            
            # Make default response
            self.response(core_mcr=default_pre_mcrs[-1], default_pre_mcrs=default_pre_mcrs[:-1], other_pre_mcrs=other_pre_mcrs)
        
        return mcrs[-1]
    
    def check_(self, mcrs: list[MCR]):
        
        core_mcr = mcrs[-1]
        dependent_mcrs = mcrs[:-1]
        
        # False if core model case has been deleted
        if not core_mcr.exists():
            return False
            
        # False if core model case is being used or used
        if core_mcr.is_used():
            return False
        
        # Check dependent model cases
        error_case_ids = []
        for mcr in dependent_mcrs:
            
            # Falseif any dependent model case is deleted (not exists)
            if not mcr.exists():
                return False
            
            if mcr.find_status(config.STATUS_ERROR):
                error_case_ids.append(mcr.id)

        # False if any dependent model case is Error
        if len(error_case_ids):
            with self.lock:
                error_log = MCR.get_simplified_error_log(core_mcr.id)
            core_mcr.update_status(config.STATUS_ERROR | config.STATUS_UNLOCK, error_log, 'w')
            return False
        
        # Lock any model case if it has not run yet
        for mcr in mcrs:
            if mcr.exists() and not mcr.is_used():
                mcr.update_status(config.STATUS_LOCK)
        
        return True
    
    def build_model_case(self, request_json: dict, dependent_case_ids: list[str] = []):
        
        mcr = MCR(self.api, request_json, self.name, dependent_case_ids)
        mcr.lock = self.lock
        return mcr._initialize()
    
    def connect_model_case(self, case_id):
        
        directory = os.path.join(config.DIR_MODEL_CASE, case_id)
        
        with self.lock:
            if not os.path.exists(directory):
                return None
            
            with open(os.path.join(directory, 'identity.json'), "r") as file:
                content = json.load(file)

        model_name = content['model']
        request_url = content['url']
        request_json = content['json']
        dependencies = content['dependencies']

        mcr = MCR(request_url, request_json, model_name, dependencies)
        mcr.lock = self.lock
        return mcr._update_call_time()

    @staticmethod
    def fetch_model_from_API(api: str):
        
        launcher = ModelLauncher(api)
        launcher.lock = Dispatcher()._lock
        return launcher
    
    @staticmethod
    def launch(lock, args: list[str]):
        
        launcher = ModelLauncher(args[0])
        launcher.lock = lock
        launcher.fire(args[1:])
