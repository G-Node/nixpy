# -*- coding: utf-8 -*-
# Copyright © 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from numbers import Integral, Real
from six import string_types

import numpy as np


BOOLS = (bool, np.bool_)


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
        if isinstance(value, BOOLS):
            return cls.Bool
        elif isinstance(value, Integral):
            return cls.Int64
        elif isinstance(value, Real):
            return cls.Float
        elif isinstance(value, string_types):
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
