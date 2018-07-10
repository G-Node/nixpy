import os
import shutil
from tempfile import mkdtemp


class TempDir(object):

    def __init__(self, prefix=None):
        self.path = mkdtemp(prefix=prefix)

    def cleanup(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def __del__(self):
        self.cleanup()
