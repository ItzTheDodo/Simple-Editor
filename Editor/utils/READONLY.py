
class ReadOnly(type):

    def __setattr__(self, name, value):
        raise ValueError
