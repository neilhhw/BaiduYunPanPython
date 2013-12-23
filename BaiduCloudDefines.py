import Queue

#File Operation

FILE_CREATE = 1
FILE_DELETE = 2
FILE_ADD    = 3
FILE_RENAME = 4
FILE_MKDIR  = 5
FILE_MODIFY = 6


#Operation Result
C_OK            =  0
C_FAIL          = -1
C_UPLOAD_FAIL   = -2
C_API_ERR       = -3

class CloudMessage():
    """message type for cloud"""
    def __init__(self, action = None, filepath = None):
        self.action = action
        self.filepath = filepath

msgQueue = Queue.Queue()
