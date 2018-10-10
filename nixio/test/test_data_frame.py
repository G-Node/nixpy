import unittest
import nixio as nix
from .tmp import TempDir
import os


class TestDataFrame(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("dataframetest")
        self.testfilename = os.path.join(self.tmpdir.path, "dataframetest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.array = self.block.create_data_frame("test array", "signal",
                                                  shape=(5,100), col_dict=nix.DataType.Double)
        self.other = self.block.create_data_frame("other array", "signal",
                                                  col_dict=nix.DataType.Double, shape=(5,100))

    def tearDown(self):
        self.file.close()
        self.tmpdir.cleanup()

    def test_data_frame_eq(self):
        pass