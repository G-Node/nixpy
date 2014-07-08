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

    def write_direct(self, data):
        self.__obj._write_data(data)

    def read_direct(self, data):
        self.__obj._read_data(data)
