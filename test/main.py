import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
SRC_DIR = os.path.join(PARENT_DIR, 'src') 

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import sbms

# Set model trigger resources of SBMS
sbms.registry.update_registry({
    '/api/v0/fe/hello': os.path.abspath('./hello.trigger.py')
})

# Init SBMS APP
sbms_app = sbms.init(
    'Hello SBMS',
    open_browser=True
)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(sbms_app.get_uvicorn_path(), host="0.0.0.0", port=8000, reload=sbms.config.APP_DEBUG)
    