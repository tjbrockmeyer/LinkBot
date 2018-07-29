

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
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) == 0 or line[0] == '#':
                    continue
                index = line.find('=')
                if index == -1 or len(line[:index]) == 0 or len(line[index:]) == 0:
                    print('Valid config lines must be in the form of "key=value".')
                    continue
                options[line[:index]] = line[index + 1:]
        return options
