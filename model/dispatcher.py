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
        
        self._lock = multiprocessing.Lock()
        self._task_queue = multiprocessing.Queue()
        self._stop_event = multiprocessing.Event()
        self._delete_queue = multiprocessing.Queue()
        self._process_manager = multiprocessing.Process(target=func, args=(self._task_queue, self._delete_queue, self._lock, self._stop_event, registry.get_registry()))
        self._process_manager.start()
    
    def dispatch(self, command):

        self._task_queue.put(command)
        
    def delete(self, case_ids: list[str]):
        
        for id in case_ids:
            self._delete_queue.put(id)
        self._task_queue.put('UPDATE')
    
    @staticmethod
    def exit():
        dispatcher = Dispatcher()
        if hasattr(dispatcher, 'stop_event'):
            dispatcher._stop_event.set()
            dispatcher._process_manager.join()
            