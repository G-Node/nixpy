# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from numbers import Number
import numpy as np

from . import util
from .entity_with_sources import EntityWithSources
from ..data_array import DataArrayMixin, DataSetMixin
from ..value import DataType
from .dimensions import (SampledDimension, RangeDimension, SetDimension,
                         DimensionType)


class DataArray(EntityWithSources, DataSetMixin, DataArrayMixin):

    def __init__(self, h5group):
        super(DataArray, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, name, type_, data_type, shape):
        newentity = super(DataArray, cls)._create_new(parent, name, type_)
        newentity._h5group.create_dataset("data", shape, data_type)
        return newentity

    def create_set_dimension(self, index):
        dimgroup = self._h5group.open_group("dimensions")
        return SetDimension._create_new(dimgroup, index)

    def create_sampled_dimension(self, index, sample):
        dimgroup = self._h5group.open_group("dimensions")
        return SampledDimension._create_new(dimgroup, index, sample)

    def create_range_dimension(self, index, range_):
        dimgroup = self._h5group.open_group("dimensions")
        return RangeDimension._create_new(dimgroup, index, range_)

    def append_set_dimension(self):
        index = len(self._h5group.open_group("dimensions")) + 1
        return self.create_set_dimension(index)

    def append_sampled_dimension(self, sample):
        index = len(self._h5group.open_group("dimensions")) + 1
        return self.create_sampled_dimension(index, sample)

    def append_range_dimension(self, range_):
        index = len(self._h5group.open_group("dimensions")) + 1
        return self.create_range_dimension(index, range_)

    def create_alias_range_dimension(self):
        if (len(self.data_extent) > 1 or
                not DataType.is_numeric_dtype(self.dtype)):
            raise ValueError("AliasRangeDimensions only allowed for 1D "
                             "numeric DataArrays.")
        if self._dimension_count() > 0:
            raise ValueError("Cannot append additional alias dimension. "
                             "There must only be one!")
        dimgroup = self._h5group.open_group("dimensions")
        data = self._h5group.group["data"]
        return RangeDimension._create_new(dimgroup, 1, data)

    def append_alias_range_dimension(self):
        return self.create_alias_range_dimension()

    def _dimension_count(self):
        return len(self._h5group.open_group("dimensions"))

    def _delete_dimension_by_pos(self, index):
        self._h5group.open_group("dimensions").delete(str(index))

    def _get_dimension_by_pos(self, index):
        h5dim = self._h5group.open_group("dimensions").open_group(str(index))
        dimtype = h5dim.get_attr("dimension_type")
        if dimtype == DimensionType.Sample:
            return SampledDimension(h5dim)
        elif dimtype == DimensionType.Range:
            return RangeDimension(h5dim)
        elif dimtype == DimensionType.Set:
            return SetDimension(h5dim)
        else:
            raise TypeError("Invalid Dimension object in file.")

    def _write_data(self, data, count, offset):
        dataset = self._h5group.get_dataset("data")
        dataset.write_data(data, count, offset)

    def _read_data(self, data, count, offset):
        dataset = self._h5group.get_dataset("data")
        dataset.read_data(data, count, offset)

    @property
    def data_extent(self):
        dataset = self._h5group.get_dataset("data")
        return dataset.shape

    @data_extent.setter
    def data_extent(self, extent):
        dataset = self._h5group.get_dataset("data")
        dataset.shape = extent

    def _get_dtype(self):
        dataset = self._h5group.get_dataset("data")
        dataset.dtype

    @property
    def dtype(self):
        return self._h5group.group["data"].dtype

    @property
    def polynom_coefficients(self):
        return tuple(self._h5group.get_data("polynom_coefficients"))

    @polynom_coefficients.setter
    def polynom_coefficients(self, coeff):
        if not coeff:
            if self._h5group.has_data("polynom_coefficients"):
                del self._h5group["polynom_coefficients"]
        else:
            dtype = DataType.Double
            self._h5group.write_data("polynom_coefficients", coeff, dtype)

    @property
    def expansion_origin(self):
        return self._h5group.get_attr("expansion_origin")

    @expansion_origin.setter
    def expansion_origin(self, eo):
        util.check_attr_type(eo, Number)
        self._h5group.set_attr("expansion_origin", eo)

    @property
    def label(self):
        return self._h5group.get_attr("label")

    @label.setter
    def label(self, l):
        util.check_attr_type(l, str)
        self._h5group.set_attr("label", l)

    @property
    def unit(self):
        return self._h5group.get_attr("unit")

    @unit.setter
    def unit(self, u):
        util.check_attr_type(u, str)
        self._h5group.set_attr("unit", u)
