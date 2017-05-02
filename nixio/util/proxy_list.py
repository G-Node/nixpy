# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)

try:
    basestring = basestring
except NameError:  # 'basestring' is undefined, must be Python 3
    basestring = (str, bytes)


class ProxyList(object):
    """
    Object that turns getters, setters etc of a NIX entity into
    something that acts like a mix between a list and a map.
    """

    def __init__(self, obj, counter, getter, index_getter, deleter):
        self.__counter = getattr(obj, counter)
        self.__getter = getattr(obj, getter)
        self.__index_getter = getattr(obj, index_getter)
        self.__deleter = getattr(obj, deleter)

    def __len__(self):
        return self.__counter()

    def __getitem__(self, key):
        if isinstance(key, basestring):
            val = None
            try:
                val = self.__getter(key)
            except:
                pass

            if val is None:
                raise KeyError("The given key does not exist: " + key)

            return val
        elif isinstance(key, int):
            count = self.__counter()

            if key < 0:
                key = count + key

            if key >= count or key < 0:
                raise KeyError("Index out of bounds: {}".format(key))

            return self.__index_getter(key)
        else:
            raise TypeError(
                "The key must be an int or a string but was: {}".format(
                    type(key)
                )
            )

    def __delitem__(self, key):
        if hasattr(key, "id"):
            key = key.id

        elem = self.__getitem__(key)
        self.__deleter(elem.id)

    def __iter__(self):
        for i in range(0, self.__counter()):
            yield self.__index_getter(i)

    def items(self):
        for i in range(0, self.__counter()):
            elem = self.__index_getter(i)
            yield (elem.id, elem)

    def __contains__(self, key):
        if hasattr(key, "id"):
            key = key.id

        if isinstance(key, basestring):
            try:
                elem = self.__getter(key)
                return elem is not None
            except:
                return False
        else:
            return False

    def __str__(self):
        str_list = [str(e) for e in list(self)]
        return "[" + ", ".join(str_list) + "]"

    def __repr__(self):
        return str(self)


class RefProxyList(ProxyList):

    def __init__(self, obj, counter, getter, index_getter, deleter, appender):
        super(RefProxyList, self).__init__(obj, counter, getter,
                                           index_getter, deleter)
        self.__appender = getattr(obj, appender)

    def append(self, key):
        if hasattr(key, "id"):
            key = key.id

        if isinstance(key, basestring):
            self.__appender(key)
        else:
            raise TypeError("The only id strings or entities can be appended")

    def extend(self, keys):
        if hasattr(keys, '__iter__'):
            [self.append(key) for key in keys]
        else:
            self.append(keys)
