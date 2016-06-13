# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity_with_sources import EntityWithSources
from ..data_array import DataSetMixin
from .h5dataset import H5DataSet


class DataSet(EntityWithSources, DataSetMixin):

    def __init__(self, h5group):
        super(DataSet, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, name, type_, data_type, shape):
        newentity = super(DataSet, cls)._create_new(parent, name, type_)
        newentity._h5dataset = H5DataSet(parent, "data", data_type, shape)
        return newentity

    def _write_data(self, data, count, offset):
        self._h5dataset.write_data(data, count, offset)

    def _read_data(self, data, count, offset):
        self._h5dataset.read_data(data, count, offset)

    @property
    def data_extent(self):
        return self._h5dataset.shape

    @data_extent.setter
    def data_extent(self, extent):
        self._h5dataset.shape = extent

    def _get_dtype(self):
        return self._h5dataset.dtype


class DataView(DataSet):

    def __init__(self):
        super(DataView, self).__init__()
