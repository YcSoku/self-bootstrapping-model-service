import os
import json
from ... import model
from ... import config
from ...util import StorageMonitor

######################################## Handler for Model Case ########################################

def handle_get_status(case_id: str):
    
    with model.Dispatcher()._lock:
        if not model.ModelCaseReference.has_case(case_id):
            return 404, f'Model Case ID ({case_id}) Not Found'
        
        return 200, {
            'status': model.ModelCaseReference.check_case_status(case_id)
        }

def handle_mc_get_error(case_id: str):
    
    with model.Dispatcher()._lock:
        if not model.ModelCaseReference.has_case(case_id):
            return 404, f'Model Case ID ({case_id}) Not Found'
        
        log = model.ModelCaseReference.get_simplified_error_log(case_id)
        return 200, log

def handle_mc_get_pre_error_cases(case_id: str):
    
    with model.Dispatcher()._lock:
        if not model.ModelCaseReference.has_case(case_id):
            return 404, f'Model Case ID ({case_id}) Not Found'
        
        cases = model.ModelCaseReference.get_pre_error_cases(case_id)
        
        return 200, {
            'case-list': cases
        }
    
def handle_mc_get_result(case_id: str):
    
    with model.Dispatcher()._lock:
        if not model.ModelCaseReference.has_case(case_id):
            return 404, f'Model Case ID ({case_id}) Not Found'
        
        response = model.ModelCaseReference.get_case_response(case_id)
        
        return 200, {
            'result': response
        }
    
def handle_mc_delete_case(case_id: str):
    
    with model.Dispatcher()._lock:
        
        if not model.ModelCaseReference.has_case(case_id):
            return 404, f'Model Case ID ({case_id}) Not Found'

    model.Dispatcher().delete([case_id])
    return 200, 'OK'

def handle_mcs_get_status(request_json: dict):
    
    with model.Dispatcher()._lock:
        case_ids = request_json['case-ids']
        status_dict = {}
    
        for case_id in case_ids:
        
            if not model.ModelCaseReference.has_case(case_id):
                return 404, f'Model Case ID ({case_id}) Not Found'
            
            status_dict[case_id] = model.ModelCaseReference.check_case_status(case_id)
    
        return 200, status_dict

def handle_mcs_get_call_status():
    
    with model.Dispatcher()._lock:
    
        response = {
            'timestamps': []
        }
        
        if not os.path.exists(config.DIR_MODEL_CASE):
            
            return response
        
        directories = os.listdir(config.DIR_MODEL_CASE)
        case_ids = [f for f in directories if os.path.isdir(os.path.join(config.DIR_MODEL_CASE, f))]
        
        for case_id in case_ids:
            
            status = 'UNLOCK'
            is_locked = model.ModelCaseReference.is_case_locked(case_id)
            if is_locked is None:
                continue
            elif is_locked:
                status = 'LOCK'
            
            time = model.ModelCaseReference.get_case_time(case_id)
                
            response['timestamps'].append({
                'id': case_id,
                'time': time,
                'status': status
            })
        
        response['timestamps'].sort(key=lambda case: case['time'], reverse=True)
            
        return response

def handle_mcs_get_serialization(request_json: dict):
    
    case_ids = request_json['case-ids']
    
    response = {
        'serialization-list': []
    }
    
    for case_id in case_ids:
        
        if not os.path.exists(os.path.join(config.DIR_MODEL_CASE, case_id)):
            return 404, f'Model Case ID ({case_id}) Not Found'
        
        with open(os.path.join(config.DIR_MODEL_CASE, case_id, 'identity.json'), 'r', encoding='utf-8') as file:
            serialization_data = json.load(file)
            response['serialization-list'].append({
                'id': case_id,
                'serialization': serialization_data
            })
    
    return 200, response

def handle_mcs_delete_cases(request_json: dict):
    
    with model.Dispatcher()._lock:
        case_ids = request_json['case-ids']
        
        delete_ids = []
        for case_id in case_ids:
            if model.ModelCaseReference.has_case(case_id):
                delete_ids.push(case_id)

    model.Dispatcher().delete(delete_ids)
    return 200, 'OK'

######################################## Handler for File System ########################################

def handle_fs_get_disk_usage():
    
    return {
        'usage': StorageMonitor().get_size()
    }

def handle_fs_get_model_case_file(case_id: str, filename: str):
    
    file_path = os.path.join(config.DIR_MODEL_CASE, case_id, 'result', filename)
    
    if not os.path.exists(file_path):
        return 404, 'Filename Not Found'
    if not model.ModelCaseReference.has_case(case_id):
        return 404, f'Model Case ID ({case_id}) Not Found'
    
    return 200, file_path

######################################## Handler for Model Runner ########################################

def handle_mr(api:str, request_json: dict):
    
    return 200, model.launcher.fetch_model_from_API(api).dispatch(request_json).make_response()

api_handlers = {
    
    # Model Case
    config.API_MC_GET_ERROR: handle_mc_get_error,
    config.API_MC_GET_STATUS: handle_get_status,
    config.API_MC_GET_RESULT: handle_mc_get_result,
    config.API_MC_DELETE_DELETE: handle_mc_delete_case,
    config.API_MC_GET_PRE_ERROR_CASES: handle_mc_get_pre_error_cases,
    
    config.API_MCS_POST_STATUS: handle_mcs_get_status,
    config.API_MCS_POST_DELETE: handle_mcs_delete_cases,
    config.API_MCS_GET_TIME: handle_mcs_get_call_status,
    config.API_MCS_POST_SERIALIZATION: handle_mcs_get_serialization,
    
    # File System
    config.API_FS_GET_DISK_USAGE: handle_fs_get_disk_usage,
    config.API_FS_GET_RESULT_FILE: handle_fs_get_model_case_file
}