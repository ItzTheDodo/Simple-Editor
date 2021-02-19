
MODES = {"dark": ["#111111", "#222222", "#333333", "#444444", "#555555", "#666666", "#777777", "#888888", "#999999"], "light": ["#ffffff", "#eeeeee", "#dddddd", "#cccccc", "#bbbbbb", "#aaaaaa", "#999999", "#888888", "#777777"]}


def createMode(name, base, linear_colour_scheme, *args):
    colours = [base]
    if linear_colour_scheme:
        step = convertDenFromHex(args[0])
        for i in range(9):
            colours.append(str(convertHex(convertDenFromHex(colours[i]) + step)))
    else:
        for i in args:
            colours.append(str(convertHex(convertDenFromHex(colours[i]) + i)))

    for i in range(len(colours)):
        colours[i] = "#" + colours[i]

    MODES[str(name)] = colours


def convertDenFromHex(num):
    a = {"a": 10, "b": 11, "c": 12, "d": 13, "e": 14, "f": 15}
    out = 0
    working = []

    for i in range(len(num)):
        curr = num[i]

        try:
            if (len(num) - 1) - i == 0:
                working.append(int(curr))
            else:
                working.append(int(curr) * pow(16, (len(num) - 1) - i))
        except ValueError:
            if (len(num) - 1) - i == 0:
                working.append(int(a[curr.lower()]))
            else:
                working.append(int(a[curr.lower()]) * pow(16, (len(num) - 1) - i))

    for i in range(len(working)):
        out += working[i]

    return out


def convertHex(num):
    return hex(num).lstrip("0x").rstrip("L")


class Font:

    def __init__(self, family, size, underline=None, bold=None):

        if not type(family) == Family:
            print("b")
            return
        if not type(size) == Size:
            print("a")
            return
        if not type(underline) == Underline and underline is not None:
            return
        if not type(bold) == Bold and bold is not None:
            print("d")
            return

        self.family = family
        self.size = size
        self.underline = underline
        self.bold = bold

    def incrementSize(self, by):
        self.size.setSize(self.size.getSize() + int(by))

    def getFont(self):
        if self.underline is None and self.bold is None:
            return self.family.getFamily(), self.size.getSize()
        elif self.underline is None:
            return self.family.getFamily(), self.size.getSize(), self.bold.getBold()
        elif self.bold is None:
            return self.family.getFamily(), self.size.getSize(), self.underline.getUnderline()
        return self.family.getFamily(), self.size.getSize(), self.underline.getUnderline(), self.bold.getBold()

    def getFamily(self):
        return self.family

    def getSize(self):
        return self.size

    def getUnderline(self):
        return self.underline

    def getBold(self):
        return self.bold

    def getRawFamily(self):
        return self.family.getFamily()

    def getRawSize(self):
        return self.size.getSize()

    def getRawUnderline(self):
        return self.underline.getUnderline()

    def getRawBold(self):
        return self.bold.getBold()


class Family(object):

    def __init__(self, family):

        self.family = str(family)

    def getFamily(self):
        return self.family

    def setFamily(self, data):
        self.family = data


class Size(object):

    def __init__(self, size):

        self.size = int(size)

    def getSize(self):
        return self.size

    def setSize(self, data):
        self.size = data


class Underline(object):

    def __init__(self):

        self.underline = 'underline'

    def getUnderline(self):
        return self.underline


class Bold(object):

    def __init__(self):

        self.bold = 'bold'

    def getBold(self):
        return self.bold


class Mode(object):

    def __init__(self, MODE):

        self.mode_name = MODE
        self.settings = MODES[self.mode_name]

    def getColours(self):
        return self.settings

    def getModeName(self):
        return self.mode_name

    def getBase(self):
        return self.settings[0]

    def getTop(self):
        return self.settings[4]
