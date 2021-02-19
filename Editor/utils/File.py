
class File(object):

    def __init__(self, path):

        self.path = path

        with open(self.path, "r") as f:
            self.in_file = f.read().split("\n")
            f.close()

    def getPath(self):
        return self.path

    def getLines(self):
        return self.in_file

    def setLines(self, lines):
        self.in_file = lines

    def save(self):
        with open(self.path, "w") as f:
            for i in self.in_file:
                f.write(i)

            f.close()

    def saveAs(self, path):
        with open(path, "w") as f:
            for i in self.in_file:
                f.write(i)

            f.close()
