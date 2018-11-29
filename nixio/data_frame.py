# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import numpy as np
from .exceptions import OutOfBounds
from .entity import Entity
from . import util
from .data_set import DataSet
from .datatype import DataType
from six import string_types
import csv


class DataFrame(Entity, DataSet):

    def __init__(self, nixparent, h5group):
        super().__init__(nixparent, h5group)
        self._sources = None
        self._columns = None
        self._rows = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, shape, col_dict, compression):
        for nam, dt in col_dict.items():
            if dt == str:
                col_dict[nam] = util.vlen_str_dtype
        dt_arr = list(col_dict.items())
        col_dtype = np.dtype(dt_arr)
        x = shape
        newentity = super(DataFrame, cls)._create_new(nixparent, h5parent, name, type_)
        newentity._h5group.create_dataset("data", (x, ), col_dtype)
        return newentity

    def append_column(self, column, name, datatype=None):
        if datatype is None:
            datatype = DataType.get_dtype(column[0])
        if datatype in string_types:
            datatype = util.vlen_str_dtype
        dt_arr = [(n, dty) for n, dty in zip(self.column_names, self.dtype)]
        dt_arr.append((name, datatype))
        dt = np.dtype(dt_arr)
        column = np.array(column, dtype=datatype)
        new_da = []
        for i, rows in enumerate(self._h5group.group['data'][:]):
            li = list(rows)
            li.append(column[i])
            tu = tuple(li)
            new_da.append(tu)
        farr = np.ascontiguousarray(new_da, dtype=dt)
        del self._h5group.group['data']
        self._h5group.group['data'] = farr
        self._h5group.create_dataset("data", (self.shape[0],), dt)
        self.write_direct(farr)

    def append_rows(self, data):
        li_data = []
        for d in data:
            d = tuple(d)
            li_data.append(d)
        pro_data = np.array(li_data, dtype=self.data_type)
        self.append(pro_data, axis=0)
        x, y = self.df_shape
        self.df_shape = tuple((x + len(data), y))

    def write_column(self, column, index=None, name=None):
        if len(column) != self.shape[0]:
            raise ValueError('If there are missing data, please fill in None')
        if not index and not name:
            raise ValueError("Either index or name must not be None")
        if name is None:
            name = self._find_name_by_idx(index)
        column = np.array(column)
        for i, rows in enumerate(self._h5group.group['data'][:]):
            cell = column[i]
            rows[name] = cell
            self.write_rows(rows=rows, index=[i])

    def read_columns(self, index=None, name=None):
        if index is None and name is None:
            raise ValueError("Either index or name must not be None")
        if name is None:
            name = []
            for ci in index:
                name.append(self.column_names[ci])
        slic = np.s_[:]
        get_col = self._read_data(sl=slic)[name]
        return get_col

    def write_rows(self, rows, index=None):
        if len(rows) != len(index):
            raise IndexError("Length of row changed and index specified do not match")
        x, = self.shape
        if max(index) > (x - 1):
            raise OutOfBounds("Row index should not exceed the existing no. of rows")
        if len(index) == 1:
            rows = tuple(rows[0])
            self._write_data(rows, sl=index)
        else:
            cr_list = []
            for i, cr in enumerate(rows):
                cr_list.append(tuple(cr))
            self._write_data(cr_list, sl=index)

    def read_rows(self, index):
        get_row = self._read_data(sl=(index,))
        return get_row

    def write_cell(self, cell, position=None, col_name=None, row_idx=None):
        if position:
            if len(position) != 2:
                raise ValueError('not a position')
            x, y = position
            targeted_row = self.read_rows(x)
            targeted_row[y] = cell
            self._write_data(targeted_row, sl=x)
        else:
            if col_name is None and row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            targeted_row = self.read_rows(row_idx)
            targeted_row[col_name] = cell
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
        row_form = "{:^10}" * (len(self.column_names) + 1)
        print(row_form.format(" ", *self.column_names))
        if self.unit:
            print(row_form.format("unit", *self.unit))
        for i, row in enumerate(self._h5group.group['data'][:]):
            print(row_form.format("Data{}".format(i), *row))

    def _find_idx_by_name(self, name):
        for i, n in enumerate(self.column_names):
            if n == name:
                return i
        return None

    def _find_name_by_idx(self, idx):
        if self.column_names[idx]:
            return self.column_names[idx]
        return None

    def row_count(self):
        count = len(self)
        return count

    def write_to_csv(self, filename, mode='w'):
        with open(filename, mode, newline='') as csvfile:
            dw = csv.DictWriter(csvfile, fieldnames=self.column_names)
            dw.writeheader()
            di = dict()  # this dict make the iter below quicker compared to using self in L172
            for n in self.column_names:
                n = str(n)
                di[n] = list(self[n])
            complete_di_list = []
            sample_len = len(self[n])
            for i in range(sample_len):
                single_sample_di = dict()
                for na in self.column_names:
                    single_sample_di[na] = di[na][i]
                complete_di_list.append(single_sample_di)
            dw.writerows(complete_di_list)
            csvfile.close()

    @property
    def unit(self):
        return self._h5group.get_attr("unit")

    @unit.setter
    def unit(self, u, column_index=None):
        col_len = len(self.dtype)
        if column_index is None:
            if len(u) != col_len:
                raise ValueError("Please specify a column index or give units for all columns")
            self._h5group.set_attr("unit", u)
        else:
            if self._h5group.get_attr("unit") is None:
                u_list = [None] * col_len
                u_list[column_index] = u
                self._h5group.set_attr("unit", u_list)
            else:
                u_list = self._h5group.get_attr("unit")
                u_list[column_index] = u
                self._h5group.set_attr("unit", u_list)

    @property
    def columns(self):
        if self.unit:
            cols = [(n, dt, u) for n, dt, u in zip(self.column_names, self.dtype, self.unit)]
        else:
            cols = [(n, dt, None) for n, dt in zip(self.column_names, self.dtype)]
        return cols

    @property
    def column_names(self):
        dt = self._h5group.group["data"].dtype
        cn = dt.fields.keys()
        return tuple(cn)

    @property
    def dtype(self):
        dt = self._h5group.group["data"].dtype
        raw_dt = dt.fields.values()
        raw_dt = list(raw_dt)
        raw_dt_list = [ele[0] for ele in raw_dt]
        return tuple(raw_dt_list)

    @property
    def df_shape(self):
        if not self._h5group.get_attr("df_shape"):
            x = len(self._h5group.group["data"])
            y = len(self.column_names)
            df_shape = (x, y)
            self._h5group.set_attr("df_shape", df_shape)
        return self._h5group.get_attr("df_shape")

    @df_shape.setter
    def df_shape(self, df_shape):
        self._h5group.set_attr("df_shape", df_shape)
