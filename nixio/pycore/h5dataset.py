# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

import numpy as np

from ..value import DataType
from . import util


class H5DataSet(object):

    def __init__(self, parent, name, dtype=None, shape=None):
        self._parent = parent
        self.name = name
        if (dtype is None) or (shape is None):
            self.dataset = self._parent[name]
        else:
            maxshape = (None,) * len(shape)
            if dtype == DataType.String:
                dtype = util.vlen_str_dtype
            self.dataset = self._parent.require_dataset(name, shape=shape,
                                                        dtype=dtype,
                                                        chunks=True,
                                                        maxshape=maxshape)

    @classmethod
    def create_from_h5obj(cls, h5obj):
        parent = h5obj.parent
        name = h5obj.name.split("/")[-1]
        return cls(parent, name)

    def write_data(self, data, count=None, offset=None):
        if count and offset:
            sl = util.co_to_slice(count, offset)
            self.dataset[sl] = data
        else:
            self.dataset[:] = data

    def read_data(self, data, count=None, offset=None):
        if 0 in self.dataset.shape or len(self.dataset.shape) == 0:
            return
        if count and offset:
            if sum(count) == 0 and len(data) == 0:
                return data
            datashape = data.shape
            sl = util.co_to_slice(count, offset)
            if (isinstance(sl, tuple) and
                    np.ndim(data) != len(sl) and
                    count[-1] == 1):
                    # data needs an extra dimension of size 1 to match slice
                    data.resize(datashape + (1,))
            self.dataset.read_direct(data, sl)
            # if data was resized, it should be returned to its original shape
            data.resize(datashape)
        else:
            self.dataset.read_direct(data)

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
