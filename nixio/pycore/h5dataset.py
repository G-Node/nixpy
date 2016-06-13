# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import numpy as np
from . import util
from ..value import DataType


class H5DataSet(object):

    def __init__(self, parent, name, dtype, shape):
        self._parent = parent
        self.name = name
        maxshape = (None,) * len(shape)
        if dtype == DataType.String:
            dtype = util.vlen_str_dtype
        self.dataset = self._parent.create_dataset(name, shape=shape,
                                                   dtype=dtype, chunks=True,
                                                   maxshape=maxshape)

    @classmethod
    def _create_from_h5obj(cls, h5obj):
        parent = h5obj.parent
        name = h5obj.name.split("/")[-1]
        return cls(parent, name)

    def write_data(self, data, count, offset):
        if count and offset:
            sl = []
            for c, o in zip(count, offset):
                sl.append(slice(o, c+o))
            if len(sl) == 1:
                sl = sl[0]
            else:
                sl = tuple(sl)
            self.dataset[sl] = data
        else:
            self.dataset[:] = data

    def read_data(self, data, count, offset):
        if count and offset:
            datashape = data.shape
            sl = []
            for c, o in zip(count, offset):
                sl.append(slice(o, c+o))
            if len(sl) == 1:
                sl = sl[0]
            else:
                sl = tuple(sl)
            if isinstance(sl, tuple) and np.ndim(data) != len(sl):
                if count[-1] == 1:
                    data.resize(datashape + (1,))
            self.dataset.read_direct(data, sl)
            data.resize(datashape)
        else:
            self.dataset.read_direct(data)

    @property
    def shape(self):
        return self.dataset.shape

    @shape.setter
    def shape(self, shape):
        self.dataset.resize(shape)

    @property
    def dtype(self):
        return self.dataset.dtype
