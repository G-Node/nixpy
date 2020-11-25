import unittest

import nixio as nix
from .tmp import TempDir
import os
import time
import numpy as np
from six import string_types
try:
    from collections.abc import OrderedDict
except ImportError:
    from collections import OrderedDict
import sys


class TestDataFrame(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("dataframetest")
        self.testfilename = os.path.join(self.tmpdir.path, "dataframetest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.df1_dtype = OrderedDict([('name', np.int64), ('id', str), ('time', float),
                                      ('sig1', np.float64), ('sig2', np.int32)])
        self.df1_data = [(1, "alpha", 20.18, 5.0, 100),
                         (2, "beta", 20.09, 5.5, 101),
                         (2, "gamma", 20.05, 5.1, 100),
                         (1, "delta", 20.15, 5.3, 150),
                         (2, "epsilon", 20.23, 5.7, 200),
                         (2, "fi", 20.07, 5.2, 300),
                         (1, "zeta", 20.12, 5.1,  39),
                         (1, "eta", 20.27, 5.1, 600),
                         (2, "theta", 20.15, 5.6, 400),
                         (2, "iota", 20.08, 5.1, 200)]
        other_arr = np.arange(11101, 11200).reshape((33, 3))
        other_di = OrderedDict({'name': np.int64, 'id': int, 'time': float})
        self.df1 = self.block.create_data_frame("test df", "signal1",
                                                data=self.df1_data, col_dict=self.df1_dtype)
        self.df2 = self.block.create_data_frame("other df", "signal2",
                                                data=self.df1_data, col_dict=self.df1_dtype)
        self.df3 = self.block.create_data_frame("reference df", "signal3",
                                                data=other_arr,
                                                col_dict=other_di)
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

    def test_create_with_list(self):
        arr = [(1, 'a', 20.18, 5.1, 100), (2, 'b', 20.09, 5.5, 101),
               (2, 'c', 20.05, 5.1, 100)]
        namelist = np.array(['name', 'id', 'time', 'sig1', 'sig2'])
        dtlist = np.array([np.int64, str, float, np.float64, np.int32])
        df_li = self.block.create_data_frame("test_list", "make_of_list",
                                             data=arr, col_names=namelist,
                                             col_dtypes=dtlist)
        assert df_li.column_names == self.df1.column_names
        assert df_li.dtype == self.df1.dtype
        for i in df_li[:]:
            self.assertIsInstance(i['id'], (bytes, string_types))
            self.assertIsInstance(i['sig2'], np.int32)

    def test_column_name_collision(self):
        arr = [(1, 'a', 20.18, 5.1, 100), (2, 'b', 20.09, 5.5, 101),
               (2, 'c', 20.05, 5.1, 100)]
        dtlist = np.array([np.int64, str, float, np.float64, np.int32])
        namelist = np.array(['name', 'name', 'name', 'name', 'name'])
        self.assertRaises(nix.exceptions.DuplicateColumnName,
                          self.block.create_data_frame,
                          'testerror', 'for_test',
                          col_names=namelist,
                          col_dtypes=dtlist, data=arr)

    def test_data_frame_type(self):
        assert self.df1.type == "signal1"
        self.df1.type = "test change"
        assert self.df1.type == "test change"

    def test_write_row(self):
        # test write single row
        row = ["1", 'abc', 3, 4.4556356242341, 5.1111111]
        assert list(self.df1[9]) == [2, b'j', 20.08, 5.1, 200]
        self.df1.write_rows([row], [9])
        assert list(self.df1[9]) == [1, b'abc', 3., 4.4556356242341, 5]
        self.assertIsInstance(self.df1[9]['name'],  np.integer)
        self.assertIsInstance(self.df1[9]['sig2'],  np.int32)
        assert self.df1[9]['sig2'] == int(5)
        # test write multiple rows
        multi_rows = [[1775, '12355', 1777, 1778, 1779],
                      [1785, '12355', 1787, 1788, 1789]]
        self.df1.write_rows(multi_rows, [1, 2])
        assert list(self.df1[1]) == [1775, b'12355', 1777, 1778, 1779]
        assert list(self.df1[2]) == [1785, b'12355', 1787, 1788, 1789]

    def test_write_column(self):
        # write by name
        column1 = np.arange(10000, 10010)
        self.df1.write_column(column1, name='sig1')
        assert list(self.df1[:]['sig1']) == list(column1)
        # write by index
        column2 = np.arange(20000, 20010)
        self.df1.write_column(column2, index=4)

        assert list(self.df1[:]['sig2']) == list(column2)

    def test_read_row(self):
        df1_array = np.array(self.df1_data, dtype=list(self.df1_dtype.items()))
        # read single row
        assert self.df1.read_rows(0) == df1_array[0]
        # read multiple
        multi_rows = self.df1.read_rows(np.arange(4, 9))
        np.testing.assert_array_equal(multi_rows, df1_array[4:9])
        multi_rows = self.df1.read_rows([3, 6])
        np.testing.assert_array_equal(multi_rows, [df1_array[3], df1_array[6]])

    def test_read_column(self):
        # read single column by index
        single_idx_col = self.df1.read_columns(index=[1])
        data = np.array([row[1] for row in self.df1_data], dtype=nix.DataType.String)
        np.testing.assert_array_equal(single_idx_col, data)

        # read multiple columns by name
        multi_col = self.df1.read_columns(name=['sig1', 'sig2'])
        data = [(row[3], row[4]) for row in self.df1_data]
        assert len(multi_col) == 10
        for data_row, df_row in zip(data, multi_col):
            assert data_row == tuple(df_row)

        # read columns with slices
        slice_cols = self.df1.read_columns(name=['sig1', 'sig2'], slc=slice(0, 6))
        data = [(row[3], row[4]) for row in self.df1_data[:6]]
        assert len(slice_cols) == 6
        for data_row, df_row in zip(data, slice_cols):
            assert data_row == tuple(df_row)

        # read single column by name
        single_idx_col = self.df1.read_columns(name=["sig2"])
        data = np.array([100, 101, 100, 150, 200, 300, 39, 600, 400, 200], dtype=nix.DataType.Int32)
        np.testing.assert_array_equal(single_idx_col, data)

        # Read multiple columns where one is string
        slice_str_cols = self.df1.read_columns(name=['id', 'sig2'], slc=slice(3, 10))
        data = [(row[1], row[4]) for row in self.df1_data[3:10]]
        assert len(slice_str_cols) == 7
        for data_row, df_row in zip(data, slice_str_cols):
            assert data_row == tuple(df_row)

    def test_read_cell(self):
        # read cell by position
        scell = self.df1.read_cell(position=[5, 3])
        assert scell == 5.2
        # read cell by row_idx + col_name
        crcell = self.df1.read_cell(col_name=['id'], row_idx=9)
        assert crcell == b'j'
        # test error raise if only one param given
        self.assertRaises(ValueError, self.df1.read_cell, row_idx=10)
        self.assertRaises(ValueError, self.df1.read_cell, col_name='sig1')

    def test_write_cell(self):
        # write cell by position
        self.df1.write_cell(105, position=[8, 3])
        assert self.df1[8]['sig1'] == 105
        # write cell by rowid colname
        self.df1.write_cell('test', col_name='id', row_idx=3)
        assert self.df1[3]['id'] == b'test'
        # test error raise
        self.assertRaises(ValueError, self.df1.write_cell, 11, col_name='sig1')

    def test_append_column(self):
        col_data = np.arange(start=16000, stop=16010, step=1)
        self.df1.append_column(col_data, name='trial_col', datatype=int)
        assert self.df1.column_names == ('name', 'id', 'time',
                                         'sig1', 'sig2', 'trial_col')
        assert len(self.df1.dtype) == 6
        k = np.array(self.df1[0:10]["trial_col"], dtype=np.int64)
        np.testing.assert_almost_equal(k, col_data)
        # too short column
        sh_col = np.arange(start=16000, stop=16003, step=1)
        with self.assertRaises(ValueError):
            self.df1.append_column(sh_col, name='sh_col')
        # too long column
        long = np.arange(start=16000, stop=16500, step=1)
        with self.assertRaises(ValueError):
            self.df1.append_column(long, name='long')

    def test_append_rows(self):
        # append single row
        srow = [1, b"test", 3, 4, 5]
        self.df1.append_rows([srow])
        assert list(self.df1[10]) == srow
        # append multi-rows
        mrows = [[1, "2", 3, 4, 5], [6, "testing", 8, 9, 10]]
        self.df1.append_rows(mrows)
        assert [list(i) for i in self.df1[-2:]] == [[1, b'2', 3., 4., 5], [6, b'testing', 8., 9., 10]]
        # append row with incorrect length
        errrow = [5, 6, 7, 8]
        self.assertRaises(ValueError, self.df1.append_rows, [errrow])

    def test_unit(self):
        assert self.df1.units is None
        self.df1.units = ["s", 'A', 'ms', 'Hz', 'mA']
        np.testing.assert_array_equal(self.df1.units,
                                      np.array(["s", 'A', 'ms', 'Hz', 'mA']))
        assert self.df2.units is None

    def test_df_shape(self):
        assert tuple(self.df1.df_shape) == (10, 5)
        # create df with incorrect dimension to see if Error is raised
        arr = np.arange(1000).reshape(10, 10, 10)
        if sys.version_info[0] == 3:
            with self.assertRaises(ValueError):
                self.block.create_data_frame('err', 'err',
                                             {'name': np.int64},
                                             data=arr)

    def test_data_type(self):
        assert self.df1.dtype[4] == np.int32
        assert self.df1.dtype[0] != self.df1.dtype[4]
        assert self.df1.dtype[2] == self.df1.dtype[3]

    def test_creation_without_name(self):
        data = np.array([("a", 1, 2.2), ("b", 2, 3.3), ("c", 3, 4.4)],
                        dtype=[('name', 'U10'), ("id", 'i4'), ('val', 'f4')])
        df = self.block.create_data_frame("without_name", "test", data=data)
        assert sorted(list(df.column_names)) == sorted(["name", "id", "val"])
        assert sorted(list(df["name"])) == ["a", "b", "c"]

    def test_timestamp_autoupdate(self):
        self.file.auto_update_timestamps = True
        df = self.block.create_data_frame("df.time", "test.time",
                                          col_dict=OrderedDict({"idx": int}))
        dftime = df.updated_at
        time.sleep(1)
        df.units = ("ly",)
        self.assertNotEqual(dftime, df.updated_at)

    def test_timestamp_noautoupdate(self):
        self.file.auto_update_timestamps = False
        df = self.block.create_data_frame("df.time", "test.time",
                                          col_dict=OrderedDict({"idx": int}))
        dftime = df.updated_at
        time.sleep(1)
        df.units = ("ly",)
        self.assertEqual(dftime, df.updated_at)
