class FileMode(object):
    ReadOnly = 'r'
    ReadWrite = 'a'
    Overwrite = 'w'


class File(object):

    def __init__(self, path, mode=FileMode.ReadWrite):
        pass

    @classmethod
    def _open(cls, path, mode=None):
        return cls(path, mode)

    def close(self):
        pass
