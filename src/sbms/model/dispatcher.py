import multiprocessing
from .. import registry
        
####################################################################################################

class Dispatcher:
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def initialize(self, func):
        
        self.lock = multiprocessing.Lock()
        self._task_queue = multiprocessing.Queue()
        self._stop_event = multiprocessing.Event()
        self._delete_queue = multiprocessing.Queue()
        self._process_manager = multiprocessing.Process(target=func, args=(self._task_queue, self._delete_queue, self.lock, self._stop_event, registry.get_registry()))
        self._process_manager.start()
    
    def dispatch(self, command):

        self._task_queue.put(command)
        
    def delete(self, case_ids: list[str]):
        
        for id in case_ids:
            self._delete_queue.put(id)
        self._task_queue.put('UPDATE')
    
    def destroy(self):
        if hasattr(self, '_stop_event'):
            
            self._stop_event.set()

            # Ensure process termination
            if self._process_manager.is_alive():
                self._process_manager.terminate()
            self._process_manager.join()

            # Close queues
            self._task_queue.close()
            self._delete_queue.close()
            self._task_queue.join_thread()
            self._delete_queue.join_thread()

            # Delete variables
            del self._task_queue
            del self._delete_queue
            del self._process_manager
            del self._stop_event
            del self.lock
            