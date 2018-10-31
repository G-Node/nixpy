# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import numpy as np
from .exceptions import OutOfBounds
from .entity import Entity
from . import util
from .data_set import DataSet


class DataFrame(Entity, DataSet):

    def __init__(self, nixparent, h5group):
        super().__init__(nixparent, h5group)
        self._sources = None
        self._columns = None
        self._rows = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, shape, col_dict, compression):
        if len(shape) != 2:
            raise ValueError("DataFrame must be 2D")
        for nam, dt in col_dict.items():
            if dt == str:
                col_dict[nam] = util.vlen_str_dtype
        cls.df_name = name
        cls.raw_shape = shape
        cls.col_names = np.array(list(col_dict.keys()))
        cls.dt_arr = list(col_dict.items())
        cls.col_dtype = np.dtype(cls.dt_arr)
        cls.col_raw_dtype = list(col_dict.values())
        x, y = shape
        newentity = super()._create_new(nixparent, h5parent, name, type_)
        newentity._h5group.create_dataset("data", (x, ), cls.col_dtype)
        return newentity

    def append_column(self, new_col, col_name, new_dt):
        if new_dt == str:
            new_dt = util.vlen_str_dtype
        self.dt_arr.append((col_name, new_dt))
        self.col_dtype = np.dtype(self.dt_arr)
        new_col = np.array(new_col, dtype=new_dt)
        self.raw_shape = tuple((self.raw_shape[0] , self.raw_shape[1]+ len(new_col)))
        new_da = []
        for i, rows in enumerate(self._h5group.group['data'][:]):
            li = list(rows)
            li.append(new_col[i])
            tu = tuple(li)
            new_da.append(tu)
        farr = np.ascontiguousarray(new_da, dtype=self.col_dtype)
        del self._h5group.group['data']
        self._h5group.group['data'] = farr
        self._h5group.create_dataset("data", (self.shape[0],), self.col_dtype)
        self.write_direct(farr)

    def append_rows(self, data):
        li_data = []
        for d in data:
            d = tuple(d)
            li_data.append(d)
        pro_data = np.array(li_data, dtype=self.col_dtype)
        self.append(pro_data, axis=0)
        self.raw_shape = tuple((self.raw_shape[0] + len(data), self.raw_shape[1]))

    def write_column(self, changed_col, col_idx=None, column_name=None):
        if len(changed_col) != self.raw_shape[0]:
            raise ValueError('If there are missing data, please fill in None')
        if not col_idx and not column_name:
            raise ValueError("Either index or name must not be None")
        if column_name is None:
            column_name = self._find_name_by_idx(col_idx)
        changed_col = np.array(changed_col)
        for i, rows in enumerate(self._h5group.group['data'][:]):
            cell = changed_col[i]
            rows[column_name] = cell
            self.write_rows(changed_row=rows, row_idx=[i])

    def read_columns(self, col_idx=None, col_name=None):
        if col_idx is None and col_name is None:
            raise ValueError("Either index or name must not be None")
        if col_name is None:
            col_name = []
            for ci in col_idx:
                col_name.append(self.col_names[ci])
        slic = np.s_[:]
        get_col = self._read_data(sl=slic)[col_name]
        return get_col

    def write_rows(self, changed_row, row_idx=None):
        if row_idx is None:
            raise ValueError("Index must be specified")
        x, y = self.raw_shape
        if max(row_idx) > (x-1):
            raise OutOfBounds("Row index should not exceed the existing no. of rows")
        if len(row_idx) == 1:
            changed_row = tuple(changed_row)
            self._write_data(changed_row, sl=row_idx)
        else:
            cr_list = []
            for i, cr in enumerate(changed_row):
                cr_list.append(tuple(cr))
            self._write_data(cr_list, sl=row_idx)

    def read_rows(self, row_idx):
        get_row = self._read_data(sl=(row_idx, ))
        return get_row

    def write_cell(self, new_item, position=None, col_name=None, row_idx=None):
        if position:
            if len(position) != 2:
                raise ValueError('not a position')
            x, y = position
            targeted_row = self.read_rows(x)
            targeted_row[y] = new_item
            self._write_data(targeted_row, sl=x)
        else:
            if col_name is None and row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            targeted_row = self.read_rows(row_idx)
            targeted_row[col_name] = new_item
            self._write_data(targeted_row, sl=row_idx)

    def read_cell(self, position=None, col_name=None, row_idx=None):
        if position:
            if len(position) != 2:
                raise ValueError('Not a position')
            x, y = position
            return self[x][y]
        else:
            if col_name is None or row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            return self[row_idx][col_name]

    def print_table(self):
        row_form = "{:^10}" * (len(self.col_names) + 1)
        print(row_form.format(" ", *self.col_names))
        if self.unit:
            print(row_form.format("unit", *self.unit))
        for i, row in enumerate(self._h5group.group['data'][:]):
            print(row_form.format("Data{}".format(i), *row))

    def _find_idx_by_name(self, name):
        for i, n in enumerate(self.col_names):
            if n == name:
                return i
        return None

    def _find_name_by_idx(self, idx):
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
    def unit(self, u, col_idx=None):
        col_len = len(self.col_dtype)
        if col_idx is None:
            if len(u) != col_len:
                raise ValueError("Please specify a column index or give units for all columns")
            self._h5group.set_attr("unit", u)
        else:
            if self._h5group.get_attr("unit") is None:
                u_list = [None] * col_len
                u_list[col_idx] = u
                self._h5group.set_attr("unit", u_list)
            else:
                u_list = self._h5group.get_attr("unit")
                u_list[col_idx] = u
                self._h5group.set_attr("unit", u_list)

    @property
    def data_type(self):
        return self._h5group.get_attr('dtype')

    @property
    def columns(self):
        if self.unit:
            cols = [(n, dt, u) for n, dt, u in zip(self.col_names, self.col_raw_dtype, self.unit)]
        else:
            cols = [(n, dt, None) for n, dt in zip(self.col_names, self.col_raw_dtype)]
        return cols
