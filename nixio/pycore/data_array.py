# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from numbers import Number
import numpy as np
from enum import Enum

from .entity_with_sources import EntityWithSources
from ..data_array import DataArrayMixin
from .data_view import DataView
from .data_set import DataSet
from ..value import DataType
from .dimensions import (SampledDimension, RangeDimension, SetDimension,
                         DimensionType)
from . import util

from .exceptions import InvalidUnit


class DataSliceMode(Enum):
    Index = 1
    Data = 2


class DataArray(EntityWithSources, DataSet, DataArrayMixin):

    def __init__(self, nixparent, h5group):
        super(DataArray, self).__init__(nixparent, h5group)

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, data_type, shape,
                    compression):
        newentity = super(DataArray, cls)._create_new(nixparent, h5parent,
                                                      name, type_)
        newentity._h5group.create_dataset("data", shape, data_type,
                                          compression)
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
        # check if existing unit is SI
        if self.unit:
            u = self.unit
            if not (util.units.is_si(u) or util.units.is_compound(u)):
                raise InvalidUnit(
                    "AliasRangeDimensions are only allowed when SI or "
                    "composites of SI units are used. "
                    "Current SI unit is {}".format(u),
                    "DataArray.append_alias_range_dimension"
                )
        return RangeDimension._create_new_alias(dimgroup, 1, self)

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
        if u:
            u = util.units.sanitizer(u)
        if u == "":
            u = None
        util.check_attr_type(u, str)
        if (self._dimension_count() == 1 and
                self.dimensions[0].dimension_type == DimensionType.Range and
                self.dimensions[0].is_alias and u is not None):
            if not (util.units.is_si(u) or util.units.is_compound(u)):
                raise InvalidUnit(
                    "[{}]: Non-SI units are not allowed if the DataArray "
                    "has an AliasRangeDimension.".format(u),
                    "DataArray.unit"
                )
        self._h5group.set_attr("unit", u)

    def get_slice(self, positions, extents=None, mode=DataSliceMode.Index):
        datadim = len(self.shape)
        if not len(positions) == datadim:
            raise IndexError("Number of positions given ({}) does not match "
                             "number of data dimensions ({})".format(
                                 len(positions), datadim
                             ))
        if extents and not len(extents) == datadim:
            raise IndexError("Number of extents given ({}) does not match "
                             "number of data dimensions ({})".format(
                                 len(extents), datadim
                             ))
        if mode == DataSliceMode.Index:
            data = np.empty(extents)
            self._read_data(data, extents, positions)
            return data
        elif mode == DataSliceMode.Data:
            return self._get_slice_bydim(positions, extents)
        else:
            raise ValueError("Invalid slice mode specified. "
                             "Supported modes are DataSliceMode.Index and "
                             "DataSliceMode.Data")

    def _get_slice_bydim(self, positions, extents):
        dpos, dext = [], []
        for dim, pos, ext in zip(self.dimensions, positions, extents):
            if dim.dimension_type in (DimensionType.Sample,
                                      DimensionType.Range):
                dpos.append(dim.index_of(pos))
                dext.append(dim.index_of(pos+ext)-dpos[-1])
            elif dim.dimension_type == DimensionType.Set:
                dpos.append(int(pos))
                dext.append(int(ext))
        data = np.empty(dext)
        self._read_data(data, dext, dpos)
        return data
