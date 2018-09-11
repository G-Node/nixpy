from __future__ import (absolute_import, division, print_function)
import numpy as np
import h5py
from .exceptions import OutOfBounds
from .entity import Entity
from . import util
from .data_set import DataSet
from .data_view import DataView


class DataFrame(Entity, DataSet):

    def __init__(self, nixparent, h5group):
        super().__init__(nixparent, h5group)
        self._sources = None
        self._columns = None
        self._rows = None
        self._col_count = None
        self._row_count = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, shape, col_dict, compression, data):
        assert len(shape) == 2, "DataFrames should always be 2 dimension"  # replace with Exception later
        cls.raw_shape = shape
        print(list(col_dict))
        cls.col_names = list(col_dict)
        cls.col_dtype = np.dtype(list(col_dict.items()))
        x,y = shape
        newentity = super()._create_new(nixparent, h5parent, name, type_)
        newentity._h5group.create_dataset("data", (x+1, y+1), cls.col_dtype)
        newentity[0, 1:] = np.array(cls.col_names)
        newentity[1:, ] = data
        print(newentity)
        return newentity

    def _read_data(self, sl=None):
        data = super()._read_data(sl)
        return data

    def setup(self, mode):  # replace the write column, write rows later
        if mode == "row":
            pass  # write data in row to row
        if mode == 'column':
            pass   # write data in columns

    def _set_columns(self, names, dtype_list):
        assert  len(names) == self.raw_shape[1], 'Not all columns are named'  # replace with Exception later
        assert  len(dtype_list) == self.raw_shape[1], 'Not all dtype of columns are set'  # replace with Exception later
        names = np.array(names)


    def add_rows(self, data):  # need to support write multiple at same time
        # experimental function for adding new rows
        assert len(data) == self.raw_shape[1]
        util.check_attr_type(data, self.col_dtype or None)
        self.append(data)
        return self

    def add_column(self, new_col, dtype):  # experimental function for adding new column
        if len(new_col) != self.data_extent[0]:
            diff = len(new_col) - self.data_extent[0]
            sl = [self.data_extent[0], len(new_col)]  # should be a slice with : not comma
            if diff < 0:
                raise IndexError  # should be Error: not all specify missing data must fill with None
            else:
                self.write_rows(data=new_col[sl]) # maybe good idea to make it auto-fill in None

        trans_arr = np.transpose(self)
        trans_arr.append(new_col)
        self = np.transpose(trans_arr)
        return self

    def write_column (self, changed_col, column_idx= None, column_name=None):
        assert len(changed_col) == self.raw_shape[0], 'if missing data, please fill None'
        if not column_idx and not column_name:
            raise IndexError  # change the error later
        if not column_idx and column_name:
            column_idx = self.find_idx_by_name(column_name) # find idx by name

        self[:, column_idx] = changed_col
        return self

    def write_rows(self, changed_row, row_idx = None, row_name = None):
        assert len(changed_row) == self.raw_shape[1]
        if not row_idx and not row_name:
            raise IndexError  # change the error later
        if not row_idx and row_name:
            row_idx = self.find_idx_by_name(row_name) # find idx by name

        self[row_idx, :] = changed_row
        return self

    def read_column(self, col_idx):  # add col_name later  # support idx as tuple slice also! later
        assert col_idx < self.raw_shape[1]
        get_col = self._read_data(sl=(col_idx))  #look through this function work in data_set
        return get_col

    def read_row(self, row_idx):
        get_row = self._read_data(sl=(row_idx, ))
        return get_row

    def write_cell(self, position):
        assert type(position) is tuple


    def read_cell(self, position):
        pass

    def columns(self):
        pass

    def rows(self):
        pass

    def find_idx_by_name(self, name):  # very inefficient change!
        for  i, n in enumerate(self.col_names):
            if n == name:
                return i
        return None
