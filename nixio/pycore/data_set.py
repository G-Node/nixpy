# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import numpy as np
from .entity_with_sources import EntityWithSources
from .util import util
from ..value import DataType


class DataSet(EntityWithSources):

    def __init__(self, h5obj):
        super(DataSet, self).__init__(h5obj)

    @classmethod
    def _create_new(cls, parent, name, type_, data_type, shape):
        newentity = super(DataSet, cls)._create_new(parent, name, type_)
        maxshape = (None,) * len(shape)
        if data_type == DataType.String:
            data_type = util.vlen_str_dtype
        newentity._h5obj.create_dataset("data", shape=shape, dtype=data_type,
                                        chunks=True, maxshape=maxshape)
        return newentity

    def _write_data(self, data, count, offset):
        # TODO: Check shape and flags
        dataset = self._h5obj["data"]
        if isinstance(data, np.ndarray) and len(data):
            if isinstance(data[0], np.bytes_):
                # TODO: convert string types
                pass

        if count and offset:
            sl = []
            for c, o in zip(count, offset):
                sl.append(slice(o, c+o))
            if len(sl) == 1:
                sl = sl[0]
            else:
                sl = tuple(sl)
            dataset[sl] = data
        else:
            dataset[:] = data

    def _read_data(self, data, count, offset):
        # TODO: Check shape and flags
        dataset = self._h5obj["data"]
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
            dataset.read_direct(data, sl)
            data.resize(datashape)
        else:
            dataset.read_direct(data)

    @property
    def data_extent(self):
        return self._h5obj["data"].shape

    @data_extent.setter
    def data_extent(self, extent):
        self._h5obj["data"].resize(extent)

    def _get_dtype(self):
        pass


class DataView(DataSet):

    def __init__(self):
        super(DataView, self).__init__()
