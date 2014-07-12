# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import DataArray
from nix.util.inject import Inject

import numpy as np

class DataArrayMixin(DataArray):

    class __metaclass__(Inject, DataArray.__class__):
        pass

    def create_data(self, shape=None, dtype=None, data=None):
        if data is None:
            if shape is None:
                raise ValueError("Either shape and or data must not be None")
            if dtype is None:
                dtype = 'f8'
        else:
            if dtype is None:
                dtype = data.dtype
            if shape is not None:
                if shape != data.shape:
                    raise ValueError("Shape must equal data.shape")
            else:
                shape = data.shape

        self._create_data(shape, dtype, data)
        return self.data

    @property
    def data(self):
        """
        A property that will give access to the DataArray's data via a DataSet
        object.

        :type: DataSet
        """
        if not self.has_data():
            return None

        if not hasattr(self, "_data"):
            setattr(self, "_data", DataSet(self))
        return self._data

    @property
    def dimensions(self):
        """
        A property containing all dimensions of a DataArray. Dimensions can be
        obtained via their index. Dimensions can be deleted from the list. Adding
        sources is done using the respective create and append methods for
        dimension descriptors. This is a read only attribute.

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

    def __delitem__(self, key):
        elem = self.__getitem__(key)
        self.__obj._delete_dimension_by_pos(elem.index)

    def __iter__(self):
        for i in range(0, len(self)):
            yield self.__obj._get_dimension_by_pos(i + 1)

    def __str__(self):
        str_list = [str(e) for e in list(self)]
        return "[" + ", ".join(str_list) + "]"

    def __repr__(self):
        return str(self)


class DataSet(object):
    """
    Data IO object for DataArray.
    """
    def __init__(self, obj):
        self.__obj = obj

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

        raw = np.empty(shape)
        self.__obj._read_data(raw, count, offset)
        return raw

    @property
    def shape(self):
        """
        :type: tupe of data array dimensions.
        """
        return self.__obj.data_extent

    @property
    def dtype(self):
        """
        :type: numpy.dtype object of the data stored in the DataArray.
        """
        return np.dtype(self.__obj._get_dtype())

    def write_direct(self, data):
        self.__obj._write_data(data, (), ())

    def read_direct(self, data):
        self.__obj._read_data(data, (), ())

    @staticmethod
    def __index_to_tuple(index):
        if index is Ellipsis:
            return ()

        tidx = type(index)
        if tidx == tuple:
            return index
        elif tidx == int or tidx == slice:
            return (index, )
        else:
            raise IndexError("Unsupported index")

    @staticmethod
    def __complete_slices(shape, index):
        if type(index) is slice:
            if index.step is not None:
                raise IndexError('Invalid index, stepping unsupported')
            if index.start is None:
                index = slice(0, index.stop)
            if index.stop is None:
                index = slice(index.start, shape)
        elif type(index) is int:
            index = slice(index, index+1)
        elif index is None:
            index = slice(0, shape)
        else:
            raise IndexError('Invalid index')
        return index

    @staticmethod
    def __fill_none(shape, index):
        size = len(shape) - len(index) + 1
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

        completed = map(self.__complete_slices, shape, index)
        combined = map(lambda s: (s.start, s.stop), completed)
        count = tuple(x[1] - x[0] for x in combined)
        offset = zip(*combined)[0]

        # drop all indices from count that came from single ints
        # NB: special case when we only have ints, e.g. (int, ) then
        # we get back the empty tuple and this is what we want,
        # because it indicates a scalar result
        squeezed = map(lambda i, c: c if type(i) != int else None, index, count)
        shape = filter(lambda x: x is not None, squeezed)

        return count, offset, shape
