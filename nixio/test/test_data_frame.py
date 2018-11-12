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
        np.testing.assert_array_equal(multi_rows, self.df1[100:150])

    def test_read_column(self):
        #read single columns by index
        single_col = self.df1.read_columns(index=[1])
        print(single_col.shape)
        #read multiple columns by name
        multi_col = self.df1.read_columns(name=['sig1','sig2'])
        print(multi_col.shape)
        print(len(multi_col[1]))

    def test_read_cell(self):
        # read cell by postion
        scell = self.df1.read_cell(position=[5,3])
        assert scell == 28
        # read cell by row_idx + col_name
        crcell = self.df1.read_cell(col_name=['id'], row_idx=22)
        assert crcell == '111'
        # test error raise if only one param given
        self.assertRaises(ValueError, lambda :self.df1.read_cell(row_idx=10))
        self.assertRaises(ValueError, lambda :self.df1.read_cell(col_name='sig1'))

    def test_write_cell(self):
        # write cell by position
        pcell = self.df1.write_cell(105, position=[111,3])
        assert self.df1[111]['sig1'] == 105
        # write cell by rowid colname
        rccell = self.df1.write_cell('test', col_name='id', row_idx=244)
        assert self.df1[244]['id'] == 'test'
        # test error raise
        self.assertRaises(ValueError, lambda: self.df1.write_cell(11, col_name='sig1'))

    def test_append_column(self):
        y = np.arange(start=16000, stop=16300, step=1)
        self.df1.append_column(y, name='trial_col', datatype=str)
        assert self.df1.column_names == ('name', 'id', 'time', 'sig1', 'sig2', 'trial_col')
        assert len(self.df1.dtype) == 6
        k = np.array(self.df1[0:300]["trial_col"], dtype=int)
        np.testing.assert_almost_equal(k, y)
        assert isinstance(self.df1[0]["trial_col"], string_types)
        # too short coulmn
        sh_col = np.arange(start=16000, stop=16100, step=1)
        self.assertRaises(IndexError, lambda : self.df1.append_column(sh_col, name='sh_col'))
        #too long column
        long = np.arange(start=16000, stop=16500, step=1)
        self.assertRaises(IndexError, lambda: self.df1.append_column(long, name='long'))


    def test_append_rows(self):
        pass

    def test_unit(self):
        assert self.df1.unit is None
        # set one unit for one column
        # set multiple
        # set all
        self.df1.unit = ["s", 'A', 'ms', 'Hz', 'mA']
        assert self.df1.unit == ["s", 'A', 'ms', 'Hz', 'mA']

        assert self.df2.unit is None



    def test_data_type(self):
        pass
