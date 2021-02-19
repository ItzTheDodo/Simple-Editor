from Editor.utils.Datafolder import DataFolder
from Editor.utils.Text import *
from Editor.Client.Editor import Client
from Editor.utils.Settings import Settings

__author__ = "Aiden"

DATAFOLDER = DataFolder()
VERSION = DATAFOLDER.getConfig().getValue("version")
DATAFOLDER.getPluginsFolder().loadPlugins(VERSION)
_MAIN_FONT = Font(Family(DATAFOLDER.getConfig().getValue("font.family")), Size(DATAFOLDER.getConfig().getValue("font.size")))
_RESOLUTION = DATAFOLDER.getConfig().getValue("client_resolution")
_MODE = Mode(DATAFOLDER.getConfig().getValue("mode"))
SETTINGS = Settings(_MAIN_FONT, _RESOLUTION, _MODE)
DATAFOLDER.getPluginsFolder().runPlugins()

from Editor.utils.Err import err

print(_MAIN_FONT.getRawFamily())
print(VERSION)
print(_RESOLUTION)
print(_MODE.getModeName())
print(_MODE.getColours())
print(DATAFOLDER.getPluginsFolder().getPlugins())

Client(VERSION, SETTINGS, err)
DATAFOLDER.getPluginsFolder().closePlugins()
exit(-1)
