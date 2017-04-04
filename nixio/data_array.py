# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

from nixio.dimension_type import DimensionType

import numpy as np


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
