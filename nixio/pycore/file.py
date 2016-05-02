class File(object):

    def __init__(self, path, mode=None):
        pass

    @classmethod
    def _open(cls, path, mode=None):
        return cls(path, mode)

    def close(self):
        pass
