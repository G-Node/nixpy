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
from .section import Section
from six import string_types
import csv


class DataFrame(Entity, DataSet):

    def __init__(self, nixfile, nixparent, h5group):
        super(DataFrame, self).__init__(nixfile, nixparent, h5group)
        self._sources = None
        self._columns = None
        self._rows = None

    @classmethod
    def create_new(cls, nixfile, nixparent, h5parent, name, type_, shape, col_dtype, compression):
        newentity = super(DataFrame, cls).create_new(nixfile, nixparent, h5parent, name, type_)
        newentity._h5group.create_dataset("data", (shape,), col_dtype, compression)
        return newentity

    def append_column(self, column, name, datatype=None):
        """
        Append a new column to the DataFrame
        In case of string, it will be better to set explicitly the datatype.

        :param column: The new column
        :type column: array-like data
        :param name: The name of new column
        :type name: str
        :param datatype: The DataType of new column
        :type datatype: DataType
        """
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
            row_list = list(rows)
            row_list.append(column[i])
            row_tuple = tuple(row_list)
            new_da.append(row_tuple)
        farr = np.ascontiguousarray(new_da, dtype=dt)
        del self._h5group.group['data']
        self._h5group.group['data'] = farr
        self._h5group.create_dataset("data", (self.shape[0],), dt)
        self.write_direct(farr)

    def append_rows(self, data):
        """
        Append a new row to the DataFrame. The data supplied must be iterable.

        :param data: The new row
        :type data: array-like data
        """
        li_data = []
        for values in data:
            values = tuple(values)
            li_data.append(values)
        pro_data = np.array(li_data, dtype=self.data_type)
        self.append(pro_data, axis=0)

    def write_column(self, column, index=None, name=None):
        """
        Overwrite an existing column.
        Either index or name of the column should be provided.

        :param column: The new column
        :type column: array-like data
        :param index: The index of the column that is written to
        :type index: string
        :param name: The name of the column that is written to
        :type name: str
        """
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

    def read_columns(self, index=None, name=None, slc=None, group_by_cols=False):
        """
        Read one or multiple (part of) column(s) in the DataFrame

        :param index: Index of column(s) to be returned
        :type index: list of int
        :param name: Name of column(s) to be returned
        :type name: list of str
        :param slc: The part of each column to be returned
        :type slc: slice
        :param group_by_cols: True for group return values by columns,
                              False for group by rows.
                              Only applicable for reading multiple columns
        :type group_by_cols: bool
        """
        if index is None and name is None:
            raise ValueError("Either index or name must not be None")
        if name is None:
            name = []
            for col_idx in index:
                name.append(self.column_names[col_idx])
        if slc is None:
            slc = np.s_[:]
        else:
            slc = np.s_[slc]
        if len(name) == 1:
            return self._read_data(slc=slc)[name[0]]
        if group_by_cols:
            gcol = list()
            for col_name in name:
                data = self._read_data(slc=slc)[col_name]
                data = [i for i in data]
                gcol.append(data)
            return np.array(gcol)

        return self._read_data(slc=slc)[name]

    def write_rows(self, rows, index):
        """
        Overwrite one or multiple existing row(s)

        :param rows: The new rows(s) and their data
        :type rows: (nested) array-like data
        :param index: Index of rows(s) to be overwritten
        :type index: list of int
        """
        if not isinstance(rows[0], (Iterable, np.void)):
            if len(index) != 1:
                raise TypeError("Rows should be in nested form")
            else:
                rows = [rows]
        if len(rows) != len(index):
            raise IndexError(
                "Number of rows ({}) does not match "
                "length of indexes ({})".format(len(rows), len(index))
            )
        n_rows, = self.shape
        if max(index) > (n_rows - 1):
            raise OutOfBounds("Row index exceeds the existing number of rows")
        if len(index) == 1:
            rows = tuple(rows[0])
            self._write_data(rows, slc=index)
        else:
            cr_list = []
            for row in rows:
                cr_list.append(tuple(row))
            self._write_data(cr_list, slc=index)

    def read_rows(self, index):
        """
        Read one or multiple row(s) in the DataFrame

        :param index: Index of row(s) to be returned
        :type index: list of int
        """
        return self[index]

    def write_cell(self, cell, position=None, col_name=None, row_idx=None):
        """
        Overwrite a cell in the DataFrame

        :param cell: The new cell
        :type cell: same type as the specified column
        :param position: Position of the targeted cell
        :type position: tuple or list or array with length 2
        :param col_name: The column name in which the targeted cell belongs to
        :type col_name: str
        :param row_idx: A length 1 list that specify on
                        which row the targeted cell is located
        :type row_idx: list of int
         """
        if position is not None:
            if len(position) != 2:
                raise ValueError("position is invalid: "
                                 "need row and column index")
            row_idx, col_idx = position
            targeted_row = self.read_rows(row_idx)
            targeted_row[col_idx] = cell
            self._write_data(targeted_row, slc=row_idx)
        else:
            if col_name is None or row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            targeted_row = self.read_rows(row_idx)
            targeted_row[col_name] = cell
            self._write_data(targeted_row, slc=row_idx)

    def read_cell(self, position=None, col_name=None, row_idx=None):
        """
        Read a cell in the DataFrame

        :param position: Position of the targeted cell
        :type position: tuple or list or array with length 2
        :param col_name: The column name in which the targeted cell belongs to
        :type col_name: str
        :param row_idx: A length 1 list that specify on
                         which row the targeted cell is located
        :type row_idx: list of int
        """
        if position is not None:
            if len(position) != 2:
                raise ValueError('Not a position')
            col_idx, row_idx = position
            return self[col_idx][row_idx]
        else:
            if col_name is None or row_idx is None:
                raise ValueError("Column and rows identifier must be given")
            cell = self[row_idx][col_name]
            cell = cell[0]
            return cell

    def print_table(self, row_sl=None, col_sl=None):
        """
        Print the whole DataFrame as a table

        :param row_sl: Rows to be printed; None for printing all rows
        :type row_sl: slice or iterable of int

        :param col_sl: Columns to be printed; None for printing all columns
        :type col_sl: slice or iterable of int
        """
        if row_sl is None:
            row_sl = np.s_[:]
        if col_sl is None:
            col_sl = np.s_[:]
        column = np.array(self.column_names)[col_sl]
        row_form = "{:^10}" * (len(column) + 1)
        print(row_form.format("column:", *column))
        if self.units is not None:
            print(row_form.format(" unit:", *self.units[col_sl]))
        if not isinstance(row_sl, Iterable):
            ridx = list(range(len(self)))[row_sl]
        else:
            ridx = row_sl
        for i, row in enumerate(self._read_data(slc=row_sl)[list(column)]):
            print(row_form.format("  [{}]:".format(ridx[i]), *row))

    def _find_idx_by_name(self, name):
        for i, col_name in enumerate(self.column_names):
            if col_name == name:
                return i
        return None

    def _find_name_by_idx(self, idx):
        if self.column_names[idx]:
            return self.column_names[idx]
        return None

    def row_count(self):
        """
        Return the total number of rows
        """
        count = len(self)
        return count

    def write_to_csv(self, filename, mode='w'):
        """
        Export the whole DataFrame to a CSV file

        :param filename: The resulted/ targeted CSV file to write to/ create
        :type filename: str
        :param mode: The column name in which the targeted cell belongs to
        :type mode: str
        """
        with open(filename, mode, newline='') as csvfile:
            if len(self.column_names) == 0:
                # no columns? return
                return
            first_col_name = self.column_names[0]
            writer = csv.DictWriter(csvfile, fieldnames=self.column_names)
            writer.writeheader()
            col_dict = dict()
            for col_name in self.column_names:
                col_name = str(col_name)
                col_dict[col_name] = list(self[col_name])
            complete_di_list = []
            sample_len = len(self[first_col_name])
            for i in range(sample_len):
                single_sample_di = dict()
                for col_name in self.column_names:
                    single_sample_di[col_name] = col_dict[col_name][i]
                complete_di_list.append(single_sample_di)
            writer.writerows(complete_di_list)
            csvfile.close()

    @property
    def units(self):
        """
        The unit of the values stored in the DataFrame.
        This is a read-write property and can be set to None.

        :type: array of str
        """
        units = self._h5group.get_attr("units")
        if units is None:
            return units
        for idx, _ in enumerate(units):
            if units[idx] == "":
                units[idx] = None
        return units

    @units.setter
    def units(self, units):
        units_arr = np.array(units, util.vlen_str_dtype)
        for idx, unit in enumerate(units_arr):
            if unit is not None:
                unit = util.units.sanitizer(unit)
                util.check_attr_type(unit, str)
                units_arr[idx] = unit
            else:
                # Write None units as empty string
                units_arr[idx] = ""
        self._h5group.set_attr("units", units_arr)
        if self.file.auto_update_timestamps:
            self.force_updated_at()

    @property
    def columns(self):
        """
        The dtype is the list of names and data types
        of all columns in the DatFrame.
        This is a read only property.

        :type: list of tuples
        """
        if np.any(self.units):
            cols = [(n, dt, u) for n, dt, u in
                    zip(self.column_names, self.dtype, self.units)]
        else:
            cols = [(n, dt, None) for n, dt in
                    zip(self.column_names, self.dtype)]
        return cols

    @property
    def column_names(self):
        """
        The dtype is the list of names of all columns in the DatFrame.
        This is a read only property.

        :type: list of str
        """
        dt = self._h5group.group["data"].dtype
        return dt.names

    @property
    def dtype(self):
        """
        The dtype is the list of DataTypes of all columns in the DatFrame.
        This is a read only property.

        :type: list of DataType
        """
        dt = self._h5group.group["data"].dtype
        key = self.column_names
        col_dict = OrderedDict()
        for k in key:
            col_dict[k] = dt.fields[k]
        raw_dt = col_dict.values()
        raw_dt = list(raw_dt)
        raw_dt_list = [ele[0] for ele in raw_dt]
        return tuple(raw_dt_list)

    @property
    def df_shape(self):
        """
        The df_shape is the shape of the DataFrame
        in (number of rows, number of columns) format.
        This is a read only property.

        :type: tuple
        """
        n_rows = len(self._h5group.group["data"])
        n_cols = len(self.column_names)
        return n_rows, n_cols

    @property
    def metadata(self):
        """
        Associated metadata of the entity. Sections attached to the entity via
        this attribute can provide additional annotations. This is an optional
        read-write property, and can be None if no metadata is available.

        :type: Section
        """
        if "metadata" in self._h5group:
            return Section(self.file, None,
                           self._h5group.open_group("metadata"))
        else:
            return None

    @metadata.setter
    def metadata(self, sect):
        if not isinstance(sect, Section):
            raise TypeError("{} is not of type Section".format(sect))
        self._h5group.create_link(sect, "metadata")

    @metadata.deleter
    def metadata(self):
        if "metadata" in self._h5group:
            self._h5group.delete("metadata")
