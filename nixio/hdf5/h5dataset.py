# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from six import ensure_str
import numpy as np
from ..datatype import DataType
from .. import util


class H5DataSet(object):

    def __init__(self, parent, name, dtype=None, shape=None,
                 compression=False):
        self._parent = parent
        self.name = name
        if (dtype is None) or (shape is None):
            self.dataset = self._parent[name]
        else:
            maxshape = (None,) * len(shape)
            if dtype == DataType.String:
                dtype = util.vlen_str_dtype
            comprargs = dict()
            if compression:
                comprargs = {"compression": "gzip", "compression_opts": 6}
            self.dataset = self._parent.require_dataset(
                name, shape=shape, dtype=dtype, chunks=True, maxshape=maxshape,
                **comprargs
            )
        self.h5obj = self.dataset

    @classmethod
    def create_from_h5obj(cls, h5obj):
        parent = h5obj.parent
        name = h5obj.name.split("/")[-1]
        return cls(parent, name)

    def write_data(self, data, slc=None):
        if data is None:  # py2compat
            data = np.full(self.shape, np.nan)[slc]
        if slc is None:
            self.dataset[:] = data
        else:
            self.dataset[slc] = data

    def read_data(self, slc=None):
        if slc is None:
            slc = slice(None, None, None)
        try:
            data = self.dataset[slc]
        except ValueError as ve_exc:
            # h5py throws ValueError for out-of-bounds index
            # Let's change it to IndexError
            raise IndexError(ve_exc)
        except TypeError as te_exc:
            # h5py 2.10 in Python2 throws TypeError for out-of-bounds index
            # Let's change it to IndexError
            raise IndexError(te_exc)
        if data.dtype == util.vlen_str_dtype:
            data = np.array([ensure_str(s) for s in data], dtype=util.vlen_str_dtype)
        elif data.dtype.fields:
            data = self._convert_string_cols(data)
        return data

    @staticmethod
    def _convert_string_cols(data):
        str_cols = list()
        for field_name, (col_type, _) in data.dtype.fields.items():
            if col_type == util.vlen_str_dtype:
                str_cols.append(field_name)

        def conv_row(row):
            for field in str_cols:
                row[field] = ensure_str(row[field])
        if str_cols:
            if not data.shape:
                # single row
                conv_row(data)
            else:
                # multiple rows
                for row in data:
                    conv_row(row)
        return data

    def set_attr(self, name, value):
        if value is None:
            if name in self.dataset.attrs:
                del self.dataset.attrs[name]
        else:
            self.dataset.attrs[name] = value

    def get_attr(self, name):
        attr = self.dataset.attrs.get(name)
        if isinstance(attr, bytes):
            attr = attr.decode()
        return attr

    @property
    def shape(self):
        return self.dataset.shape

    @shape.setter
    def shape(self, shape):
        self.dataset.resize(shape)

    @property
    def dtype(self):
        dtype = self.dataset.dtype
        if dtype == util.vlen_str_dtype:
            return DataType.String
        return dtype

    def __str__(self):
        return "<H5DataSet object: {}>".format(self.dataset.name)
