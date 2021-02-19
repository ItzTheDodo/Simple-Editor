from Editor.utils.Plugin import Plugin
from Editor.utils.Text import *


class EditorPlugin(Plugin):

    def __init__(self, VERSION):
        Plugin.__init__(self, VERSION)

    def onLoad(self):
        createMode("custom", "00ff00", True, "110011")
