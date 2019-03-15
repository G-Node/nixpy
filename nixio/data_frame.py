# -*- coding: utf-8 -*-
# Copyright © 2019, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
from collections import OrderedDict
from inspect import isclass
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
        super(DataFrame, self).__init__(nixparent, h5group)
        self._sources = None
        self._columns = None
        self._rows = None

    @classmethod
    def _create_new(cls, nixparent, h5parent,
                    name, type_, shape, col_dtype, compression):
        newentity = super(DataFrame, cls)._create_new(nixparent, h5parent,
                                                      name, type_)
        newentity._h5group.create_dataset("data", (shape, ), col_dtype)
        return newentity

    def append_column(self, column, name, datatype=None):
        # datatype is better included for strings
        if len(column) < len(self):
            raise ValueError("Not enough entries for column in this dataframe")
        elif len(column) > len(self):
            raise ValueError("Too much entries for column in this dataframe")
        if datatype is None:
            datatype = DataType.get_dtype(column[0])
        if isclass(datatype) and any(issubclass(datatype, st)
                                     for st in string_types):
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
        # In Python2, the data supplied must be iterable (not np arrays)
        li_data = []
        for d in data:
            d = tuple(d)
            li_data.append(d)
        pro_data = np.array(li_data, dtype=self.data_type)
        self.append(pro_data, axis=0)

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
            self.write_rows(rows=[rows], index=[i])

    # TODO: for read column add a Mode that break down the tuples
    def read_columns(self, index=None, name=None, sl=None):
        if index is None and name is None:
            raise ValueError("Either index or name must not be None")
        if name is None:
            name = []
            for ci in index:
                name.append(self.column_names[ci])
        if sl is None:
            slic = np.s_[:]
        else:
            slic = np.s_[sl]
        get_col = self._read_data(sl=slic)[name]
        if len(name) == 1:
            get_col = [i[0] for i in get_col]
        return get_col

    def write_rows(self, rows, index):
        if len(rows) != len(index):
            raise IndexError(
                "Number of rows ({}) does not match "
                "length of indexes ({})".format(len(rows), len(index))
            )
        x, = self.shape
        if max(index) > (x - 1):
            raise OutOfBounds(
                "Row index exceeds the existing number of rows"
            )
        if len(index) == 1:
            rows = tuple(rows[0])
            self._write_data(rows, sl=index)
        else:
            cr_list = []
            for i, cr in enumerate(rows):
                cr_list.append(tuple(cr))
            self._write_data(cr_list, sl=index)

    def read_rows(self, index):
        if isinstance(index, Iterable):
            index = list(index)
        get_row = self._read_data(sl=(index,))
        return get_row

    def write_cell(self, cell, position=None, col_name=None, row_idx=None):
        if position is not None:
            if len(position) != 2:
                raise ValueError("position is invalid: "
                                 "need row and column index")
            x, y = position
            targeted_row = self.read_rows(x)
            targeted_row[y] = cell
            self._write_data(targeted_row, sl=x)
        else:
            if col_name is None or row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            targeted_row = self.read_rows(row_idx)
            targeted_row[col_name] = cell
            self._write_data(targeted_row, sl=row_idx)

    def read_cell(self, position=None, col_name=None, row_idx=None):
        if position is not None:
            if len(position) != 2:
                raise ValueError('Not a position')
            x, y = position
            return self[x][y]
        else:
            if col_name is None or row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            cell = self[row_idx][col_name]
            cell = cell[0]
            return cell

    def print_table(self):
        row_form = "{:^10}" * (len(self.column_names) + 1)
        print(row_form.format(" ", *self.column_names))
        if self.units:
            print(row_form.format("unit", *self.units))
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
            di = dict()
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
    def units(self):
        return self._h5group.get_attr("units")

    @units.setter
    def units(self, u):
        for i in u:
            i = util.units.sanitizer(i)
            util.check_attr_type(i, str)
        u = np.array(u, dtype=util.vlen_str_dtype)
        self._h5group.set_attr("units", u)

    @property
    def columns(self):
        if self.units:
            cols = [(n, dt, u) for n, dt, u in
                    zip(self.column_names, self.dtype, self.units)]
        else:
            cols = [(n, dt, None) for n, dt in
                    zip(self.column_names, self.dtype)]
        return cols

    @property
    def column_names(self):
        dt = self._h5group.group["data"].dtype
        return dt.names

    @property
    def dtype(self):
        dt = self._h5group.group["data"].dtype
        key = self.column_names
        di = OrderedDict()
        for k in key:
            di[k] = dt.fields[k]
        raw_dt = di.values()
        raw_dt = list(raw_dt)
        raw_dt_list = [ele[0] for ele in raw_dt]
        return tuple(raw_dt_list)

    @property
    def df_shape(self):
        x = len(self._h5group.group["data"])
        y = len(self.column_names)
        df_shape = (x, y)
        df_shape = tuple(df_shape)
        self._h5group.set_attr("df_shape", df_shape)
        return self._h5group.get_attr("df_shape")
