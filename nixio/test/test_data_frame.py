import unittest
import nixio as nix
from .tmp import TempDir
import os
import numpy as np

# TODO: add test for dict vs name_list + dt_list creation
# TODO: add test for multiple reading and multiple writing (if supported)

@unittest.skip
class TestDataFrame(unittest.TestCase):

    def setUp(self):
        di = {'name': int, 'id': str, 'time': float}
        arr = np.arange(999).reshape((333, 3))
        self.tmpdir = TempDir("dataframetest")
        self.testfilename = os.path.join(self.tmpdir.path, "dataframetest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.df = self.block.create_data_frame("test array", "signal",
                                                  shape=(50, 100), col_dict=di)

    def tearDown(self):
        self.file.close()
        self.tmpdir.cleanup()

    def create_with_list(self):
        arr = np.arange(999).reshape((333, 3))
        namelist = np.array(['name', 'id', 'time'])
        dtlist = np.array([int, str, float])
        new_df = self.block.create_data_frame('test1', 'for_test',
                                    col_names=namelist, col_dtypes=dtlist, shape=(333, 3), data=arr)

    def test_data_frame_eq(self):
        pass

    def test_write_row(self):
        pass

    def test_write_column(self):
        pass

    def test_read_row(self):
        pass

    def test_read_column(self):
        pass

    def test_read_cell(self):
        pass

    def test_write_cell(self):
        pass

    def test_unit(self):
        pass

    def test_append_column(self):
        y = np.arange(start=1333, stop=1666, step=1)
        self.df.append_column(y, name='trail_col', datatype=str)
