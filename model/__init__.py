import queue
import multiprocessing

from .. import config
from .dispatcher import Dispatcher
from .modelCaseReference import ModelCaseReference
from .modelLauncher import model_status_controller_sync, ModelLauncher as launcher

def monitoring(task_queue: queue.Queue[any], delete_queue: queue.Queue[any], lock, stop_event, registry):
    
    print('Model dispatcher is working', flush=True)
    
    process_dict = {}
    deferred_queue = []
    execution_set = set()
    
    LAUNCH_READY        =       0b1
    LAUNCH_NOT_READY    =       0b10
    LAUNCH_ERROR        =       0b100
    LAUNCH_CANCEL       =       0b1000
    
    # Remove completed or error model cases
    def update_execution_set():
        with lock:
            execution_set.intersection_update({ id for id in execution_set if ModelCaseReference.has_case(id) and not ModelCaseReference.is_case_done(id) })
    
    def try_to_launch(command):
        
        core_mc_id = command[-1]
        update_execution_set()
        
        if len(execution_set) <= config.MAX_RUNNING_MODEL_CASE_NUM and core_mc_id not in execution_set:
            
            execution_set.add(core_mc_id)
            process = multiprocessing.Process(target=launcher.launch, args=(lock, command + [registry[command[0]]]))
            process_dict[core_mc_id] = process
            process.start()
            
            return True
        
        return False
    
    def check_(command: list[str]):
         
        core_mc_id = command[-1]
        depdent_mc_ids = command[1:-1]
        
        with lock:
            
            # Cancel if core model case itself has been deleted
            if not ModelCaseReference.has_case(core_mc_id):
                return LAUNCH_CANCEL
            
            # Check dependent cases if they are done
            for id in depdent_mc_ids:
                    
                    # Cancel if any dependent model case has been deleted
                    if not ModelCaseReference.has_case(id):
                        ModelCaseReference.delete_case(core_mc_id)
                        return LAUNCH_CANCEL
                    
                    # Get status
                    current_status = ModelCaseReference.get_case_status(id)
                
                    # Error if any dependent case is error
                    if (current_status & config.STATUS_ERROR) == config.STATUS_ERROR:
                        
                        error_log = ModelCaseReference.get_simplified_error_log(core_mc_id)
                        ModelCaseReference.update_case_status(core_mc_id, config.STATUS_ERROR | config.STATUS_UNLOCK, error_log, 'w')
                        return LAUNCH_ERROR
                    
                    # Not ready if any dependent case is not completed 
                    if (current_status & config.STATUS_COMPLETE) != config.STATUS_COMPLETE:
                        return LAUNCH_NOT_READY
            
            return LAUNCH_READY
    
    def execute_(command: list[str]):
        
        # Command to trigger a round of task loop (but do nothing)
        if command == 'UPDATE':
            return
        
        check_code = check_(command)
        
        if check_code == LAUNCH_READY:
            if not try_to_launch(command):
                deferred_queue.append(command)
                
        elif check_code == LAUNCH_NOT_READY:
            deferred_queue.append(command)
    
    def waiting():
    
        command = task_queue.get()
        task_queue.put(command)
        
    def delete_model_cases():
        
        with lock:
            while not stop_event.is_set():
                try:
                    
                    case_id = delete_queue.get_nowait()
                    
                    # Terminate running model case
                    if case_id in process_dict:
                        process_dict[case_id].terminate()
                        process_dict[case_id].join()
                        del process_dict[case_id]
                        
                    if case_id in execution_set:
                        execution_set.remove(case_id)
                        
                    ModelCaseReference.delete_case(case_id)
                
                except queue.Empty:
                    break
    
    # Task loop
    try:
        while not stop_event.is_set():
            
            delete_model_cases()
            
            try:
                command = task_queue.get_nowait()
                execute_(command)
            
            except queue.Empty:
                
                while deferred_queue:
                    task_queue.put(deferred_queue.pop(0))
                waiting()
            
    except KeyboardInterrupt:
        print('Model dispatcher stopped', flush=True)
