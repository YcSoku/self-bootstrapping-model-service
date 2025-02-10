import os

APP_PORT                                        =       8000
APP_DEBUG                                       =       True

# API Version           
API_VERSION                                     =       '/api/v0'

# API for Model Case            
API_MC_DELETE_DELETE                            =       API_VERSION + '/mc'
API_MC_GET_ERROR                                =       API_VERSION + '/mc/error'
API_MC_GET_STATUS                               =       API_VERSION + '/mc/status'
API_MC_GET_RESULT                               =       API_VERSION + '/mc/result'
API_MC_GET_PRE_ERROR_CASES                      =       API_VERSION + '/mc/pre-error-cases'

API_MCS_POST_DELETE                             =       API_VERSION + '/mcs'
API_MCS_GET_TIME                                =       API_VERSION + '/mcs/time'
API_MCS_POST_STATUS                             =       API_VERSION + '/mcs/status'
API_MCS_POST_SERIALIZATION                      =       API_VERSION + '/mcs/serialization'

# API for File System           
API_FS_GET_DISK_USAGE                           =       API_VERSION + '/fs/usage'
API_FS_GET_RESULT_ZIP                           =       API_VERSION + '/fs/result/zip'
API_FS_GET_RESULT_FILE                          =       API_VERSION + '/fs/result/file'

# API for Model Runner
API_MR                                          =       API_VERSION + '/{category}/{model_name}'

# API for docs
API_DOCS                                        =       '/docs'

# Status Flag           
STATUS_UNLOCK                                   =       0b1
STATUS_LOCK                                     =       0b10
STATUS_RUNNING                                  =       0b100
STATUS_COMPLETE                                 =       0b1000
STATUS_NONE                                     =       0b10000
STATUS_ERROR                                    =       0b100000
STATUS_DELETE                                   =       0b1000000

# Directory Setting         
DIR_ROOT                                        =       os.path.dirname(os.path.abspath(__file__))
DIR_MODEL_CASE                                  =       os.path.join(DIR_ROOT, 'case')
DIR_MODEL                                       =       os.path.join(DIR_ROOT, 'model')

DIR_RESOURCE_MODEL                              =       os.path.join(DIR_ROOT, 'resource', 'model')
DIR_RESOURCE_MODEL_TRIGGER                      =       os.path.join(DIR_ROOT, 'resource', 'trigger')
DIR_STORAGE_LOG                                 =       os.path.join(DIR_ROOT, 'resource', 'storage', 'log.txt')

APP_IGNORE_THINGS                               =       [
                                                            '.DS_Store',
                                                            '__MACOSX'
                                                        ]

CAL_CORE_NUM                                    =       5
MAX_RUNNING_MODEL_CASE_NUM                      =       20
