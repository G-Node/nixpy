# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from numbers import Number

from .entity_with_sources import EntityWithSources
from ..data_array import DataArrayMixin, DataSetMixin
from ..value import DataType
from .dimensions import (SampledDimension, RangeDimension, SetDimension,
                         DimensionType)
from . import util

from .exceptions import InvalidUnit


class DataSet(DataSetMixin):

    def _write_data(self, data, count, offset):
        dataset = self._h5group.get_dataset("data")
        dataset.write_data(data, count, offset)

    def _read_data(self, data, count, offset):
        dataset = self._h5group.get_dataset("data")
        dataset.read_data(data, count, offset)

    @property
    def data_extent(self):
        """
        The size of the data.

        :type: set of int
        """
        dataset = self._h5group.get_dataset("data")
        return dataset.shape

    @data_extent.setter
    def data_extent(self, extent):
        dataset = self._h5group.get_dataset("data")
        dataset.shape = extent

    @property
    def data_type(self):
        """
        The data type of the data stored in the DataArray. This is a read only
        property.

        :type: DataType
        """
        return self._get_dtype()

    def _get_dtype(self):
        dataset = self._h5group.get_dataset("data")
        return dataset.dtype


class DataArray(EntityWithSources, DataSet, DataArrayMixin):

    def __init__(self, nixparent, h5group):
        super(DataArray, self).__init__(nixparent, h5group)

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, data_type, shape):
        newentity = super(DataArray, cls)._create_new(nixparent, h5parent,
                                                      name, type_)
        newentity._h5group.create_dataset("data", shape, data_type)
        return newentity

    def _read_data(self, data, count, offset):
        coeff = self.polynom_coefficients
        origin = self.expansion_origin
        if len(coeff) or origin:
            if not origin:
                origin = 0.0

            super(DataArray, self)._read_data(data, count, offset)
            util.apply_polynomial(coeff, origin, data)
        else:
            super(DataArray, self)._read_data(data, count, offset)

    def append_set_dimension(self):
        """
        Append a new SetDimension to the list of existing dimension
        descriptors.

        :returns: The newly created SetDimension.
        :rtype: SetDimension
        """
        dimgroup = self._h5group.open_group("dimensions")
        index = len(dimgroup) + 1
        return SetDimension._create_new(dimgroup, index)

    def append_sampled_dimension(self, sampling_interval):
        """
        Append a new SampledDimension to the list of existing dimension
        descriptors.

        :param sampling_interval: The sampling interval of the SetDimension
                                  to create.
        :type sampling_interval: float

        :returns: The newly created SampledDimension.
        :rtype: SampledDimension
        """
        dimgroup = self._h5group.open_group("dimensions")
        index = len(dimgroup) + 1
        return SampledDimension._create_new(dimgroup, index, sampling_interval)

    def append_range_dimension(self, ticks):
        """
        Append a new RangeDimension to the list of existing dimension
        descriptors.

        :param ticks: The ticks of the RangeDimension to create.
        :type ticks: list of float

        :returns: The newly created RangeDimension.
        :rtype: RangeDimension
        """
        dimgroup = self._h5group.open_group("dimensions")
        index = len(dimgroup) + 1
        return RangeDimension._create_new(dimgroup, index, ticks)

    def append_alias_range_dimension(self):
        """
        Append a new RangeDimension that uses the data stored in this
        DataArray as ticks. This works only(!) if the DataArray is 1-D and
        the stored data is numeric. A ValueError will be raised otherwise.

        :returns: The created dimension descriptor.
        :rtype: RangeDimension
        """
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

    def delete_dimensions(self):
        """
        Delete all the dimension descriptors for this DataArray.
        """
        dimgroup = self._h5group.open_group("dimensions")
        ndims = len(dimgroup)
        for idx in range(ndims):
            del dimgroup[str(idx+1)]
        return True

    def _dimension_count(self):
        return len(self._h5group.open_group("dimensions"))

    def _get_dimension_by_pos(self, index):
        h5dim = self._h5group.open_group("dimensions").open_group(str(index))
        dimtype = h5dim.get_attr("dimension_type")
        if dimtype == DimensionType.Sample:
            return SampledDimension(h5dim, index)
        elif dimtype == DimensionType.Range:
            return RangeDimension(h5dim, index)
        elif dimtype == DimensionType.Set:
            return SetDimension(h5dim, index)
        else:
            raise TypeError("Invalid Dimension object in file.")

    @property
    def dtype(self):
        """
        The data type of the data stored in the DataArray.
        This is a read only property.

        :return: DataType
        """
        return self._h5group.group["data"].dtype

    @property
    def polynom_coefficients(self):
        """
        The polynomial coefficients for the calibration. By default this is
        set to a {0.0, 1.0} for a linear calibration with zero offset.
        This is a read-write property and can be set to None

        :type: list of float
        """
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
        """
        The expansion origin of the calibration polynomial.
        This is a read-write property and can be set to None.
        The default value is 0.

        :type: float
        """
        return self._h5group.get_attr("expansion_origin")

    @expansion_origin.setter
    def expansion_origin(self, eo):
        util.check_attr_type(eo, Number)
        self._h5group.set_attr("expansion_origin", eo)

    @property
    def label(self):
        """
        The label of the DataArray. The label corresponds to the label of the
        x-axis of a plot. This is a read-write property and can be set to
        None.

        :type: str
        """
        return self._h5group.get_attr("label")

    @label.setter
    def label(self, l):
        util.check_attr_type(l, str)
        self._h5group.set_attr("label", l)

    @property
    def unit(self):
        """
        The unit of the values stored in the DataArray. This is a read-write
        property and can be set to None.

        :type: str
        """
        return self._h5group.get_attr("unit")

    @unit.setter
    def unit(self, u):
        util.check_attr_type(u, str)
        if u is not None:
            u = util.units.sanitizer(u)
            if not (util.units.is_si(u) or util.units.is_compound(u)):
                raise InvalidUnit(
                    "{} is not SI or composite of SI units".format(u),
                    "DataArray.unit"
                )
        self._h5group.set_attr("unit", u)
