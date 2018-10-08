# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import numpy as np
from .exceptions import OutOfBounds
from .entity import Entity
from . import util
from .data_set import DataSet
from .data_view import DataView
# TODO add slicing param for functions


class DataFrame(Entity, DataSet):

    def __init__(self, nixparent, h5group):
        super().__init__(nixparent, h5group)
        self._sources = None
        self._columns = None
        self._rows = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, shape, col_dict, compression):
        if len(shape) != 2: raise ValueError("Dataframe must be 2D")
        for name, type in col_dict.items():
            if type == str:
                col_dict[name] = util.vlen_str_dtype
        cls.raw_shape = shape
        cls.col_names = np.array(list(col_dict.keys()))
        dt_arr = list(col_dict.items())
        cls.col_dtype = np.dtype(dt_arr)
        cls.col_raw_dtype = list(col_dict.values())
        x,y = shape
        newentity = super()._create_new(nixparent, h5parent, name, type_)
        newentity._h5group.create_dataset("data", (x, ), cls.col_dtype)
        return newentity

    def _read_data(self, sl=None):  # Done
        data = super()._read_data(sl)
        return data

    def append_rows(self, data):  # need to support write multiple at same time
        # experimental function for adding new rows
        if len(data) != self.raw_shape[1]:
            raise ValueError("No of items in new row is not correct")
        util.check_attr_type(data, self.col_dtype)
        self.append(data)
        return self

    def append_column(self, new_col, dtype):  # experimental function for adding new column
        if len(new_col) != self.data_extent[0]:
            diff = len(new_col) - self.data_extent[0]
            sl = [self.data_extent[0], len(new_col)]  # should be a slice with : not comma
            if diff < 0:
                raise ValueError("No of items in new column is not correct")
            else:
                self.write_rows(data=new_col[sl]) # maybe good idea to make it auto-fill in None

        trans_arr = np.transpose(self)
        trans_arr.append(new_col)
        self['data'] = np.transpose(trans_arr)
        return self

    def write_column(self, changed_col, col_idx= None, column_name=None):  # Done
        if len(changed_col) != self.raw_shape[0]:
            raise  ValueError('if missing data, please fill None')
        if not col_idx and not column_name:
            raise ValueError("Either index or name must not be None")
        if column_name is None:
            column_name = self.find_name_by_idx(col_idx)  # find name by name
        changed_col = np.array(changed_col)
        for i, rows in enumerate(self._h5group.group['data'][:]):
            cell = changed_col[i]
            rows[column_name] = cell
            self.write_rows(changed_row=rows, row_idx=i)
        return self

    def read_columns(self, col_idx= None, col_name=None):  #Done
        if col_idx is None and col_name is None:
            raise ValueError("Either index or name must not be None")
        if col_name is None:
            col_name = []
            for ci in col_idx:
                col_name.append(self.col_names[ci])
        slice = np.s_[:]
        get_col = self._read_data(sl=slice)[col_name]
        return get_col

    def write_rows(self, changed_row, row_idx = None):  # Done!
        if row_idx is None:
            raise ValueError("Index must be specified")
        x, y = self.raw_shape
        if max(row_idx) > (x-1):
            raise OutOfBounds("Row index should not exceed the existing no. of rows")
        if len(row_idx) == 1:
            changed_row = tuple(changed_row)
            self._write_data(changed_row, sl=row_idx)
            return self
        else:
            cr_list = []
            for i, cr in enumerate(changed_row):
               cr_list.append(tuple(cr))
            self._write_data(cr_list,sl=row_idx)
            return self

    def read_rows(self, row_idx):  # Done
        get_row = self._read_data(sl=(row_idx, ))
        return get_row

    def write_cell(self, new_item, position= None, col_name=None, row_idx=None):  #Done
        # TODO force the dtype to be inline
        if position:
            if len(position) != 2: raise ValueError('not a position')
            x, y = position
            targeted_row = self.read_row(x)
            targeted_row[y] = new_item
            self._write_data(targeted_row, sl=x)
            return self
        else:
            if col_name is None and row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            targeted_row = self.read_row(row_idx)
            targeted_row[col_name] = new_item
            self._write_data(targeted_row,sl=row_idx)
            return self

    def read_cell(self, position= None, col_name=None, row_idx=None):  # Done
        if position:
            if len(position) != 2: raise ValueError('not a position')
            x, y = position
            return self[x][y]
        else:
            if col_name is None or row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            return self[row_idx][col_name]

    def find_idx_by_name(self, name):
        for  i, n in enumerate(self.col_names):
            if n == name:
                return i
        return None

    def find_name_by_idx(self, idx):
        for i, n in enumerate(self.col_names):
            if i == idx:
                return n
        return None

    def row_count(self):
        count = len(self)
        return count

    @property
    def unit(self):
        return self._h5group.get_attr("unit")

    @unit.setter
    def unit(self, u):
        if len(u) != len(self.col_dtype):
            raise ValueError("Length mismatched")
        self._h5group.set_attr("unit", u)

    @property
    def data_type(self):
        return self._h5group.get_attr('dtype')

    @data_type.setter
    def data_type(self):
        dt = self.col_dtype
        self._h5group.set_attr('dtype', dt)

    @property
    def column(self):
        return self.dtype

