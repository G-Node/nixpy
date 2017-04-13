# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from numbers import Number
import numpy as np
import sys

from .entity_with_sources import EntityWithSources
from ..value import DataType
from .dimensions import (SampledDimension, RangeDimension, SetDimension,
                         DimensionType)
from . import util

from .exceptions import InvalidUnit


class DataArrayMixin(object):

    @property
    def data(self):
        """
        DEPRECATED DO NOT USE ANYMORE! Returns self

        :type: :class:`~nixio.data_array.DataArray`
        """
        import warnings
        warnings.warn("Call to deprecated property DataArray.data",
                      category=DeprecationWarning)
        return self

    @property
    def dimensions(self):
        """
        A property containing all dimensions of a DataArray. Dimensions can be
        obtained via their index. Adding dimensions is done using the
        respective append methods for dimension descriptors.
        This is a read only attribute.

        :type: ProxyList of dimension descriptors.
        """
        if not hasattr(self, "_dimensions"):
            setattr(self, "_dimensions", DimensionProxyList(self))
        return self._dimensions

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        """
        Overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class,
        implemented or escaped
        """
        return hash(self.id)


class SetDimensionMixin(object):

    dimension_type = DimensionType.Set


class RangeDimensionMixin(object):

    dimension_type = DimensionType.Range


class SampleDimensionMixin(object):

    dimension_type = DimensionType.Sample


class DimensionProxyList(object):
    """
    List proxy for the dimensions of a data array.
    """

    def __init__(self, obj):
        self.__obj = obj

    def __len__(self):
        return self.__obj._dimension_count()

    def __getitem__(self, key):
        if isinstance(key, int):
            length = self.__obj._dimension_count()

            if key < 0:
                key = length + key

            if key >= length or key < 0:
                raise KeyError("Index out of bounds: " + str(key))

            return self.__obj._get_dimension_by_pos(key + 1)
        else:
            raise TypeError("The key must be an int but was: " + type(key))

    def __iter__(self):
        for i in range(0, len(self)):
            yield self.__obj._get_dimension_by_pos(i + 1)

    def __str__(self):
        str_list = [str(e) for e in list(self)]
        return "[" + ", ".join(str_list) + "]"

    def __repr__(self):
        return str(self)


class DataSetMixin(object):
    """
    Data IO object for DataArray.
    """

    def __array__(self):
        raw = np.empty(self.shape, dtype=self.dtype)
        self.read_direct(raw)
        return raw

    def __getitem__(self, index):
        index = self.__index_to_tuple(index)
        if len(index) < 1:
            return np.array(self)
        # if we got to here we have a tuple with len >= 1
        count, offset, shape = self.__tuple_to_count_offset_shape(index)
        raw = np.empty(shape, dtype=self.dtype)

        self._read_data(raw, count, offset)

        return raw

    def __setitem__(self, index, value):
        index = self.__index_to_tuple(index)
        if len(index) < 1:
            shape = self.shape
            count, offset = shape, tuple([0]*len(shape))
        else:
            count, offset, _ = self.__tuple_to_count_offset_shape(index)

        # NB: np.ascontiguousarray does not copy the array if it is
        # already in c-contiguous form
        raw = np.ascontiguousarray(value)
        self._write_data(raw, count, offset)

    def __len__(self):
        s = self.len()

        # PyObject_Size returns a Py_ssize_t, which is the same as the
        # systems size_t type but signed, i.e. ssize_t. (cf. PEP 0353)
        # The maximum positive integer that Py_ssize_t can hold is
        # exposed via sys.maxsize.
        # Since self.shape can contain longs we need to check for that
        if s > sys.maxsize:
            estr = ("DataSet's shape[0] is too big for Python's __len__. "
                    "Use DataSet.len() instead")
            raise OverflowError(estr)
        return s

    def __iter__(self):
        for idx in range(self.len()):
            yield self[idx]

    def len(self):
        """
        Length of the first dimension. Equivalent to `DataSet.shape[0]`.

        :type: int or long
        """
        return self.shape[0]

    @property
    def shape(self):
        """
        :type: tuple of data array dimensions.
        """
        return self.data_extent

    @property
    def size(self):
        """
        Number of elements in the DataSet, i.e. the product of the
        elements in :attr:`~nixio.data_array.DataSet.shape`.

        :type: int
        """
        return np.prod(self.shape)

    @property
    def dtype(self):
        """
        :type: :class:`numpy.dtype` object holding type infromation about
               the data stored in the DataSet.
        """
        return np.dtype(self._get_dtype())

    def write_direct(self, data):
        """
        Directly write all of ``data`` to the
        :class:`~nixio.data_array.DataSet`.  The supplied data must be a
        :class:`numpy.ndarray` that matches the DataSet's shape and must have
        C-style contiguous memory layout (see :attr:`numpy.ndarray.flags` and
        :class:`~numpy.ndarray` for more information).

        :param data: The array which contents is being written
        :type data: :class:`numpy.ndarray`
        """
        self._write_data(data, (), ())

    def read_direct(self, data):
        """
        Directly read all data stored in the :class:`~nixio.data_array.DataSet`
        into ``data``. The supplied data must be a :class:`numpy.ndarray` that
        matches the DataSet's shape, must have C-style contiguous memory layout
        and must be writeable (see :attr:`numpy.ndarray.flags` and
        :class:`~numpy.ndarray` for more information).

        :param data: The array where data is being read into
        :type data: :class:`numpy.ndarray`
        """

        self._read_data(data, (), ())

    def append(self, data, axis=0):
        """
        Append ``data`` to the DataSet along the ``axis`` specified.

        :param data: The data to append. Shape must agree except for the
        specified axis
        :param axis: Along which axis to append the data to
        """
        data = np.ascontiguousarray(data)

        if len(self.shape) != len(data.shape):
            raise ValueError(
                "Data and DataArray must have the same dimensionality"
            )

        if any([s != ds for i, (s, ds) in
                enumerate(zip(self.shape, data.shape)) if i != axis]):
            raise ValueError("Shape of data and shape of DataArray must match "
                             "in all dimension but axis!")

        offset = tuple(0 if i != axis else x for i, x in enumerate(self.shape))
        count = data.shape
        enlarge = tuple(self.shape[i] + (0 if i != axis else x)
                        for i, x in enumerate(data.shape))
        self.data_extent = enlarge
        self._write_data(data, count, offset)

    @staticmethod
    def __index_to_tuple(index):
        tidx = type(index)

        if tidx == tuple:
            return index
        elif tidx == int or tidx == slice:
            return (index, )
        elif tidx == type(Ellipsis):
            return ()
        else:
            raise IndexError("Unsupported index")

    @staticmethod
    def __complete_slices(shape, index):
        if type(index) is slice:
            if index.step is not None:
                raise IndexError('Invalid index, stepping unsupported')
            start = index.start
            stop = index.stop
            if start is None:
                start = 0
            elif start < 0:
                start = shape + start
            if stop is None:
                stop = shape
            elif stop < 0:
                stop = shape + stop
            index = slice(start, stop, index.step)
        elif type(index) is int:
            if index < 0:
                index = shape + index
                index = slice(index, index+1)
            else:
                index = slice(index, index+1)
        elif index is None:
            index = slice(0, shape)
        else:
            raise IndexError('Invalid index')
        return index

    @staticmethod
    def __fill_none(shape, index, to_replace=1):
        size = len(shape) - len(index) + to_replace
        return tuple([None] * size)

    def __tuple_to_count_offset_shape(self, index):
        # precondition: type(index) == tuple and len(index) >= 1
        fill_none = self.__fill_none
        shape = self.shape

        if index[0] is Ellipsis:
            index = fill_none(shape, index) + index[1:]
        if index[-1] is Ellipsis:
            # if we have a trailing ellipsis we just cut it away
            # and let complete_slices do the right thing
            index = index[:-1]

        # here we handle Ellipsis in the middle of the tuple
        # we *can* only handle one, if there are more, then
        # __complete_slices will raise a InvalidIndex error
        pos = index.index(Ellipsis) if Ellipsis in index else -1
        if pos > -1:
            index = index[:pos] + fill_none(shape, index) + index[pos+1:]

        # in python3 map does not work with None therefore if
        # len(shape) != len(index) we wont get the expected
        # result. We therefore need to fill up the missing values
        index = index + fill_none(shape, index, to_replace=0)

        completed = list(map(self.__complete_slices, shape, index))
        combined = list(map(lambda s: (s.start, s.stop), completed))
        count = tuple(x[1] - x[0] for x in combined)
        offset = [x for x in zip(*combined)][0]

        # drop all indices from count that came from single ints
        # NB: special case when we only have ints, e.g. (int, ) then
        # we get back the empty tuple and this is what we want,
        # because it indicates a scalar result
        squeezed = map(lambda i, c: c if type(i) != int
                       else None, index, count)
        shape = list(filter(lambda x: x is not None, squeezed))

        return count, offset, shape

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
        util.check_attr_type(u, str)
        if u is not None:
            u = util.units.sanitizer(u)
            if not (util.units.is_si(u) or util.units.is_compound(u)):
                raise InvalidUnit(
                    "{} is not SI or composite of SI units".format(u),
                    "DataArray.unit"
                )
        self._h5group.set_attr("unit", u)
