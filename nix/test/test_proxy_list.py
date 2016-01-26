# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function, unicode_literals)

import unittest

from nix import *
from nix.util.proxy_list import ProxyList

try:
    basestring = basestring
except NameError:  # 'basestring' is undefined, must be Python 3
    basestring = (str,bytes)


class WithIdMock(object):

    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class, implemented or escaped
        """
        return hash(self.id)


class WithListMock(object):

    def __init__(self, l):
        self.__dict = dict([(str(i), WithIdMock(str(i))) for i in range(l)])
        self.__list = ProxyList(self, "count", "get", "get", "delete")

    def get(self, id):
        return self.__dict[str(id)]

    def count(self):
        return len(self.__dict)

    def delete(self, id):
        del self.__dict[str(id)]

    @property
    def list(self):
        return self.__list


class TestProxyList(unittest.TestCase):

    def setUp(self):
        self.mock = WithListMock(5)

    def test_proxy_list_len(self):
        assert(len(self.mock.list) == 5)

    def test_proxy_list_getitem(self):

        length = len(self.mock.list)
        for i in range(length):
            assert(self.mock.list[i] == self.mock.list[i - length])
            assert(self.mock.list[str(i)] == self.mock.list[i])

        self.assertRaises(KeyError, lambda : self.mock.list["notexist"])
        self.assertRaises(KeyError, lambda : self.mock.list[-1 - length])
        self.assertRaises(KeyError, lambda : self.mock.list[length])
        self.assertRaises(TypeError, lambda : self.mock.list[3.14])

    def test_proxy_list_delitem(self):
        del self.mock.list["4"]
        assert(len(self.mock.list) == 4)
        del self.mock.list[3]
        assert(len(self.mock.list) == 3)
        del self.mock.list[WithIdMock("2")]
        assert(len(self.mock.list) == 2)

    def test_proxy_list_contains(self):
        assert("2" in self.mock.list)
        assert("notexist" not in self.mock.list)
        assert(WithIdMock("2") in self.mock.list)
        assert(WithIdMock("notexist") not in self.mock.list)
        assert(42 not in self.mock.list)

    def test_proxy_list_iterators(self):
        assert(len(list(self.mock.list)) == 5)
        assert(len(dict(self.mock.list.items())) == 5)

    def test_proxy_list_str(self):
        assert(isinstance(str(self.mock.list), basestring))
        assert(isinstance(repr(self.mock.list), basestring))
