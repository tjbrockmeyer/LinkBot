

class IniIO(dict):
    trues = ['1', 't', 'true']

    def int(self, op):
        return int(self[op])

    def float(self, op):
        return float(self[op])

    def str(self, op):
        return self[op]

    def bool(self, op):
        return self[op] in IniIO.trues

    def get_int(self, op, default=0):
        try:
            return self.int(op)
        except KeyError:
            return default

    def get_float(self, op, default=0.0):
        try:
            return self.float(op)
        except KeyError:
            return default

    def get_str(self, op, default=''):
        try:
            return self[op]
        except KeyError:
            return default

    def get_bool(self, op, default=False):
        try:
            return self.bool(op)
        except KeyError:
            return default

    @staticmethod
    def load(filepath):
        options = IniIO()
        section = None
        with open(filepath, 'r') as f:
            for (i, line) in enumerate(f):
                line = line.strip()
                if not line or line[0] == '#' or line[0] == ';':
                    continue
                if line.startswith('['):
                    index = line.find(']')
                    if index == -1:
                        raise IOError('File {}, Line {}    Valid section headers must be in the form of "[section]"'
                                      .format(filepath, i + 1))
                    section = line[1:index]
                    continue
                index = line.find('=')
                if index == -1 or not line[:index].rstrip():
                    raise IOError('File {}, Line {}    Valid properties must be in the form of "key=value"'
                                  .format(filepath, i + 1))
                options[("{}.".format(section) if section is not None else '')
                        + line[:index].rstrip()] = line[index + 1:]
        return options
