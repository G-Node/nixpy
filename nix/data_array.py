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

    class __metaclass__(Inject):
        pass

    @property
    def dimensions(self):
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
