
class Settings(object):

    def __init__(self, text, resolution, setup):

        self.text = text
        self.resolution = resolution
        self.setup = setup

    def getText(self):
        return self.text

    def getRes(self):
        return self.resolution

    def getSetup(self):
        return self.setup
