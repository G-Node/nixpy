import unittest
import nixio as nix
from .tmp import TempDir
import os
import numpy as np
from six import string_types, integer_types

# TODO: add test for multiple reading and multiple writing (if supported)


class TestDataFrame(unittest.TestCase):

    def setUp(self):

        self.tmpdir = TempDir("dataframetest")
        self.testfilename = os.path.join(self.tmpdir.path, "dataframetest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        di = {'name': int, 'id': str, 'time': float, 'sig1': np.float64, 'sig2': np.int32}
        arr = np.arange(1500).reshape((300, 5))
        other_arr = np.arange(11101, 11200).reshape((33, 3))
        other_di = {'name': int, 'id': str, 'time': float}
        self.df1 = self.block.create_data_frame("test df", "signal1",
                                                data=arr, col_dict=di)
        self.df2 = self.block.create_data_frame("other df", "signal2",
                                               data=other_arr, col_dict=other_di)
        self.df3 = self.block.create_data_frame("reference df", "signal3",
                                                data=arr, col_dict=di)
        self.dtype = self.df1._h5group.group["data"].dtype

    def tearDown(self):
        self.file.close()
        self.tmpdir.cleanup()

    def test_data_frame_eq(self):
        assert self.df1 == self.df1
        assert not self.df1 == self.df2
        assert self.df2 == self.df2
        assert self.df1 is not None
        assert self.df2 is not None

    def test_shape(self):
        print(self.df1.df_shape)
        assert self.df1.df_shape ==  (300, 5)
        # create df with incorrect dimension to see if Error is raised
        arr = np.arange(100).reshape(100)

    def test_create_with_list(self):
        arr = np.arange(1500).reshape((300, 5))
        namelist = np.array(['name', 'id', 'time', 'sig1', 'sig2'])
        dtlist = np.array([int, str, float, np.float64, np.int32])
        df_li = self.block.create_data_frame("test_list", "make_of_list", data=arr,
                                             col_names=namelist, col_dtypes=dtlist)
        assert df_li.column_names == self.df1.column_names
        assert df_li.dtype == self.df1.dtype
        for i in df_li[:]:
            self.assertIsInstance(i['id'], str)
            self.assertIsInstance(i['sig2'], np.int32)

    def test_data_frame_type(self):
        assert self.df1.type == "signal1"
        self.df1.type = "test change"
        assert self.df1.type == "test change"

    def test_write_row(self):
        # test write single row
        row = ["1",'abc',3,4.4556356242341,5.1111111]
        self.assertAlmostEqual(list(self.df1[11]),
                               [55, '56', 57., 58., 59], "Contents or dtype incorrect")
        self.df1.write_rows([row], [11])
        assert list(self.df1[11]) == [1, 'abc',3. ,4.4556356242341, 5]
        self.assertIsInstance(self.df1[11]['name'],  np.integer)
        self.assertIsInstance(self.df1[11]['sig2'],  np.int32)
        assert self.df1[11]['sig2'] == int(5)
        # test write multiple rows
        multi_rows = [[1775,1776,1777,1778,1779], [1785,1786,1787,1788,1789]]
        self.df1.write_rows(multi_rows, [1,2])
        assert list(self.df1[1]) == [1775,'1776',1777,1778,1779]
        assert list(self.df1[2]) == [1785,'1786',1787,1788,1789]

    def test_write_column(self):
        # write by name
        column1 = np.arange(10000, 10300)
        self.df1.write_column(column1, name='sig1')
        assert list(self.df1[:]['sig1']) == list(column1)
        # write by index
        column2 = np.arange(20000, 20300)
        self.df1.write_column(column2, index=4)
        assert list(self.df1[:]['sig2']) == list(column2)

    def test_read_row(self):
        # read single row
        assert list(self.df1.read_rows(0)) == [0,'1',2,3,4]
        # read multiple
        multi_rows = self.df1.read_rows(np.arange(100,150))
        assert list(multi_rows) == list(self.df1[100:150])

    def test_read_column(self):
        pass

    def test_read_cell(self):
        pass

    def test_write_cell(self):
        pass

    def test_unit(self):
        assert self.df1.unit is None
        # set one unit for one column
        # set multiple
        # set all
        self.df1.unit = ["s", 'A', 'ms', 'Hz', 'mA']
        assert self.df1.unit == ["s", 'A', 'ms', 'Hz', 'mA']

        assert self.df2.unit is None

    def test_append_column(self):
        y = np.arange(start=1600, stop=1900, step=1)
        self.df1.append_column(y, name='trail_col', datatype=str)

    def test_data_type(self):
        pass
