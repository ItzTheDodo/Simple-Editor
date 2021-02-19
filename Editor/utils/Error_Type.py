
class ErrorType(object):

    def __init__(self, code, msg):

        self.code = code
        self.msg = msg

    def getMSG(self):
        return self.msg

    def getCode(self):
        return self.code


class EditorException(Exception):

    def __init__(self, t):

        self.message = t.getMSG()
        super().__init__(self.message)
        self.errors = t.getCode()

    def printException(self):
        print("Editor Error [" + str(self.errors) + "]: " + self.message)


EDITOR_ERROR_INVALID_TYPE = ErrorType(1, "variable datatype")
EDITOR_ERROR_FILE_UNREADABLE = ErrorType(2, "file type unreadable")
EDITOR_ERROR_TOO_MANY_FILES = ErrorType(3, "there are too many files open")
EDITOR_ERROR_PARALLEL_RUN_DISALLOW = ErrorType(4, "parrallel running is not allowed in config")
