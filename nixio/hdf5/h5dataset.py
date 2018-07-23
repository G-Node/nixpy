# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
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

    def write_data(self, data, sl=None):
        if sl is None:
            self.dataset[:] = data
        else:
            self.dataset[sl] = data

    def read_data(self, sl=None):
        if sl is None:
            return self.dataset[:]
        try:
            return self.dataset[sl]
        except ValueError as ve:
            # h5py throws ValueError for out-of-bounds index
            # Let's change it to IndexError
            raise IndexError(ve)

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
        return self.dataset.dtype

    def __str__(self):
        return "<H5DataSet object: {}>".format(self.dataset.name)
