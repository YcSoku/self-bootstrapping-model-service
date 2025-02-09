import os
import portalocker

class StorageMonitor:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        
        if cls._instance is None:
            
            cls._instance = super().__new__(cls)
            
        return cls._instance
        
    def initialize(self, folder_paths: list[str], log_file: str):
        
        print('Storage Monitor is Working!', flush=True)
        
        if not os.path.exists(log_file):
            directory_path = os.path.dirname(log_file)
            os.makedirs(directory_path)
        with open(log_file, 'w') as f:
            f.write('')
        
        self.log_file = log_file
        self.folder_paths = folder_paths
        self.total_size_gb = self.calculate_folder_size()
    
    def calculate_folder_size(self):
        
        for folder_path in self.folder_paths:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
        return total_size / (1024 ** 3)

    def check_size(self):
        with open(self.log_file, 'r+') as f:
            try:
                portalocker.lock(f, portalocker.LOCK_EX)

                size_changes = (float(line.strip()) for line in f if line.strip())

                for change in size_changes:
                    self.total_size_gb += change

                f.seek(0)
                f.truncate()
                
            finally:
                portalocker.unlock(f)

        return self.total_size_gb
    
    def get_size(self):
        
        return self.check_size()
    
    def destroy(self):
        StorageMonitor._instance = None
    
def update_size(log_file: str, size_change_gb: float):
    
    with open(log_file, 'a') as f:
        
        portalocker.lock(f, portalocker.LOCK_EX)
        f.write(f"{size_change_gb}\n")
        portalocker.unlock(f) 
