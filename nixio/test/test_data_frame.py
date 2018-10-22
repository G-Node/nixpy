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

    def test_write_row(self):
        pass

    def test_write_col(self):
        pass

    def test_read_row(self):
        pass

    def test_read_col(self):
        pass

    def test_read_cell(self):
        pass

    def test_write_cell(self):
        pass

    def test_unit(self):
        pass
