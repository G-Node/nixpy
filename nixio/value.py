# Copyright (c) 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)
from numbers import Number, Integral, Real

import numpy as np

strings = (str, bytes)
try:
    strings += (basestring,)
except NameError:
    pass

bools = (bool, np.bool_)

valid_types = (Number, strings, bools)


class DataType(object):
    UInt8 = np.uint8
    UInt16 = np.uint16
    UInt32 = np.uint32
    UInt64 = np.uint64
    Int8 = np.int8
    Int16 = np.int16
    Int32 = np.int32
    Int64 = np.int64
    Float = np.float_
    Double = np.double
    String = np.string_
    Bool = np.bool_

    @classmethod
    def get_dtype(cls, value):
        if isinstance(value, bools):
            return cls.Bool
        elif isinstance(value, Integral):
            return cls.Int64
        elif isinstance(value, Real):
            return cls.Float
        elif isinstance(value, strings):
            return cls.String
        else:
            raise ValueError("Unknown type for value {}".format(value))

    @classmethod
    def is_numeric_dtype(cls, dtype):
        return (dtype == cls.Int8 or
                dtype == cls.Int16 or
                dtype == cls.Int32 or
                dtype == cls.Int64 or
                dtype == cls.UInt8 or
                dtype == cls.UInt16 or
                dtype == cls.UInt32 or
                dtype == cls.UInt64 or
                dtype == cls.Float or
                dtype == cls.Double)


class Value(object):

    def __init__(self, value):
        if isinstance(value, valid_types):
            self.value = value
        else:
            raise TypeError("Invalid value type: {}".format(type(value)))
        self.uncertainty = 0
        self.reference = ""
        self.filename = ""
        self.encoder = ""
        self.checksum = ""
        self.data_type = DataType.get_dtype(value)

    def __str__(self):
        return "Value{{[{dtype}] {value}}}".format(dtype=self.data_type,
                                                   value=self.value)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if hasattr(other, "value"):
            return self.value == other.value
        else:
            return self.value == other
