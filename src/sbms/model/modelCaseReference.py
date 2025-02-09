import os
import json
import datetime
from .. import util
from .. import config


######################################## Utils ########################################
        
def get_error_case_ids_in_log(case_id: str):
    
    error_log = ModelCaseReference.get_status_log(case_id)
    if error_log == None:
        return []
    
    return error_log.split('\n')[0].split('-')

######################################## Model Case Reference ########################################

class ModelCaseReference:
    
    def __init__(self, request_url: str, request_json: dict, model_name: str, dependent_case_ids: list[str] = []):
     
        self.lock = None
        self.model_name = model_name
        self.request_url = request_url
        self.request_json = request_json
        self.dependencies = dependent_case_ids
        
        self.id = util.generate_md5(request_url + json.dumps(request_json))
        self.directory = os.path.join(config.DIR_MODEL_CASE, self.id)
        self.local_file_locker = os.path.join(self.directory, 'lock')
    
    def _update_call_time(self):
        
        current_time = datetime.datetime.now()
        current_timestamp = int(current_time.timestamp() * 1000)
            
        with self.lock:
            
            old_timestamp =  int(util.get_filenames(os.path.join(self.directory, 'time'))[0])
            old_name = os.path.join(self.directory, 'time', f'{old_timestamp}')
            new_name = os.path.join(self.directory, 'time', f'{current_timestamp}')
            os.rename(old_name, new_name)
            
            return self
    
    def _initialize(self):
        
        with self.lock:
        
            if os.path.exists(self.directory):
                return self
            
            os.makedirs(self.directory)
            os.mkdir(os.path.join(self.directory, 'time'))
            os.mkdir(os.path.join(self.directory, 'result'))
            os.mkdir(os.path.join(self.directory, 'status'))
                
            # Serialize request
            content = {
                'model': self.model_name,
                'url': self.request_url,
                'json': self.request_json,
                'dependencies': self.dependencies,
            }
            with open(os.path.join(self.directory, 'identity.json'), 'w', encoding = 'utf-8') as file:
                json.dump(content, file, indent = 4)
            
            current_time = datetime.datetime.now()
            current_timestamp = int(current_time.timestamp() * 1000)
            with open(os.path.join(self.directory, 'time', f'{current_timestamp}'), 'w', encoding = 'utf-8') as file:
                pass
            
            with open(os.path.join(self.directory, 'status', f'{config.STATUS_UNLOCK}'), 'w', encoding = 'utf-8') as file:
                file.write('OK')
            
            with open(os.path.join(self.directory, 'response.json'), 'w', encoding = 'utf-8') as file:
                json.dump({
                    'model': self.model_name,
                    'case-id': self.id,
                }, file, indent = 4)
            
            return self

    def exists(self):
        
        with self.lock:  
            if os.path.exists(os.path.join(config.DIR_MODEL_CASE, self.id)): 
                return True
            return False
          
    def is_used(self): 
            
        with self.lock:
            
            path = os.path.join(self.directory, 'status')
            filenames = util.get_filenames(path)
            self.status = int(filenames[0])
            
            is_completed = (self.status & config.STATUS_COMPLETE) == config.STATUS_COMPLETE
            is_error = (self.status & config.STATUS_ERROR) == config.STATUS_ERROR
            is_locked = (self.status & config.STATUS_LOCK) == config.STATUS_LOCK
            
            result = is_completed or is_error or is_locked
            

            return result
     
    def find_status(self, status):
        
        with self.lock:
            
            path = os.path.join(self.directory, 'status')
            filenames = util.get_filenames(path)
            self.status = int(filenames[0])
            
            result = (self.status & status) == status
            
            return result
    
    def update_status(self, status, content=None, mode = 'a'):
            
        path = os.path.join(self.directory, 'status')
        
        with self.lock:
            
            filenames = util.get_filenames(path)
            self.status = int(filenames[0])
            
            if self.status == status:
                return
            
            old_name = os.path.join(self.directory, 'status', f'{self.status}')
            new_name = os.path.join(self.directory, 'status', f'{status}')
            self.status = status
            
            util.rename_file(old_name, new_name, f'CHANGE MCR ({self.model_name}: {self.id}) status to {status}')
            
            if not content == None:
                
                write_content = ''
                write_content += (f'{content}' + '\n')
                
                with open(new_name, mode, encoding='utf-8') as file:
                    file.write(write_content)

    def make_response(self, content=None):
        
        response_file_path = os.path.join(self.directory, 'response.json')
        
        with self.lock:
            if content is not None: 
                    
                content['case-id'] = self.id
                content['model'] = self.model_name
            
                with open(response_file_path, 'w', encoding = 'utf-8') as file:
                    json.dump(content, file, indent = 4)
            
            else:
                with open(response_file_path, 'r', encoding='utf-8') as file:
                    content = json.load(file)
                
            return content
    
    @staticmethod
    def get_simplified_error_log(case_id: str):
        
        id_set = set()
        id_stack = util.Stack()
        
        # Initialize error-id stack
        for id in ModelCaseReference.get_case_dependencies(case_id):
            if ModelCaseReference.has_case(id) and ModelCaseReference.is_case_error(id):
                id_stack.push(id)
        
        # Stack recursion
        while not id_stack.is_empty():
            
            error_id = id_stack.pop()
            id_set.add(error_id)
            
            for id in ModelCaseReference.get_case_dependencies(error_id):
                if ModelCaseReference.has_case(id) and ModelCaseReference.is_case_error(id):
                    id_stack.push(id)
        
        error_log = ''
        for id in id_set:
            
            error_log += f'=== Error Happened When Model Case ({ModelCaseReference.get_model_name(id)}: {id}) Running ===\n{ModelCaseReference.get_status_log(id)}\n'

        return error_log
    
    @staticmethod
    def get_model_name(case_id: str):
        
        with open(os.path.join(config.DIR_MODEL_CASE, case_id, 'identity.json'), 'r', encoding='utf-8') as file:
            model_name = json.load(file)['model']
        return model_name
    
    @staticmethod
    def get_case_dependencies(case_id: str):
        
        with open(os.path.join(config.DIR_MODEL_CASE, case_id, 'identity.json'), 'r', encoding='utf-8') as file:
            dependencies = json.load(file)['dependencies']
        return dependencies
    
    @staticmethod
    def has_case(case_id: str):
        
        if os.path.exists(os.path.join(config.DIR_MODEL_CASE, case_id)): 
            return True
        return False
    
    @staticmethod
    def delete_case(case_id: str):
            
        directory = os.path.join(config.DIR_MODEL_CASE, case_id)
        if not os.path.exists(directory):
            return False
        
        util.update_size(config.DIR_STORAGE_LOG, -util.get_folder_size_in_gb(directory))
        util.delete_folder_contents(directory)
        return True
    
    @staticmethod
    def is_case_locked(case_id: str):

        path = os.path.join(config.DIR_MODEL_CASE, case_id, 'status')
        if not os.path.exists(path):
            return None
            
        filenames = util.get_filenames(path)
        status_code = int(filenames[0])

        if (status_code & config.STATUS_LOCK) == config.STATUS_LOCK:
            return True
        return False
    
    @staticmethod
    def get_case_time(case_id: str):
            
        time = int(util.get_filenames(os.path.join(config.DIR_MODEL_CASE, case_id, 'time'))[0])
        
        return time
    
    @staticmethod
    def get_case_status(case_id: str):
            
        current_status = int(util.get_filenames(os.path.join(config.DIR_MODEL_CASE, case_id, 'status'))[0])
        
        return current_status

    @staticmethod
    def check_case_status(case_id: str):
            
        current_status = int(util.get_filenames(os.path.join(config.DIR_MODEL_CASE, case_id, 'status'))[0])
        
        if (current_status & config.STATUS_COMPLETE) == config.STATUS_COMPLETE:
            return 'COMPLETE'
        if (current_status & config.STATUS_RUNNING) == config.STATUS_RUNNING:
            return 'RUNNING'
        if (current_status & config.STATUS_ERROR) == config.STATUS_ERROR:
            return 'ERROR'
        if (current_status & config.STATUS_NONE) == config.STATUS_NONE:
            return 'NONE'
        if (current_status & config.STATUS_UNLOCK) == config.STATUS_UNLOCK:
            return 'UNLOCK'
        if (current_status & config.STATUS_LOCK) == config.STATUS_LOCK:
            return 'LOCK'
    
    @staticmethod
    def get_case_response(case_id: str):

        response_file_path = os.path.join(config.DIR_MODEL_CASE, case_id, 'response.json')
            
        with open(response_file_path, 'r', encoding='utf-8') as file:
            content = json.load(file)
        
        return content
    
    @staticmethod
    def get_status_log(case_id: str):
        
        if not os.path.exists(os.path.join(config.DIR_MODEL_CASE, case_id, 'status')):
            return None
        
        status_code = util.get_filenames(os.path.join(config.DIR_MODEL_CASE, case_id, 'status'))[0]
        with open(os.path.join(config.DIR_MODEL_CASE, case_id, 'status', status_code), 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    
    @staticmethod
    def update_case_status(case_id: str, new_status_code: int, content=None, mode = 'a'):
            
        case_status_directory = os.path.join(config.DIR_MODEL_CASE, case_id, 'status')
        status_code = util.get_filenames(case_status_directory)[0]
    
        if new_status_code == status_code:
            return
        
        old_name = os.path.join(case_status_directory, f'{status_code}')
        new_name = os.path.join(case_status_directory, f'{new_status_code}')
        
        util.rename_file(old_name, new_name, f'CHANGE MCR ({ModelCaseReference.get_model_name(case_id)}: {case_id}) status to {new_status_code}')
        
        if not content == None:
            
            write_content = ''
            write_content += (f'{content}' + '\n')
            
            with open(new_name, mode, encoding='utf-8') as file:
                file.write(write_content)
    
    @staticmethod
    def get_pre_error_cases(case_id: str):
        
        id_set = { case_id }
        id_stack = util.Stack()
        
        # Initialize error-id stack
        for case_id in get_error_case_ids_in_log(case_id):
            if ModelCaseReference.has_case(case_id):
                id_stack.push(case_id)
        
        # Stack recursion
        while not id_stack.is_empty():
            
            error_id = id_stack.pop()
            id_set.add(error_id)
            
            for case_id in get_error_case_ids_in_log(error_id):
                if ModelCaseReference.has_case(case_id):
                    id_stack.push(case_id)

        return list(id_set)
        
    @staticmethod
    def is_case_error(case_id: str):
        
        case_status_directory = os.path.join(config.DIR_MODEL_CASE, case_id, 'status')
        current_status = int(util.get_filenames(case_status_directory)[0])
    
        is_error = (current_status & config.STATUS_ERROR) == config.STATUS_ERROR
        
        return is_error
    
    @staticmethod
    def is_case_done(case_id: str):
            
        current_status = int(util.get_filenames(os.path.join(config.DIR_MODEL_CASE, case_id, 'status'))[0])
        is_completed = (current_status & config.STATUS_COMPLETE) == config.STATUS_COMPLETE
        is_error = (current_status & config.STATUS_ERROR) == config.STATUS_ERROR
        
        return is_completed or is_error
