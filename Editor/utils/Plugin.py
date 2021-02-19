from _thread import *


class Plugin:

    def __init__(self, VERSION):

        self.VERSION = VERSION

    def onRun(self):
        pass

    def onLoad(self):
        pass

    def onClose(self):
        exit_thread()
