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
from packaging import version

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
    Float = np.float32
    Double = np.double
    if version.parse(np.__version__) < version.parse("2.0"):
        String = np.unicode_
    else:
        String = np.str_
    Bool = np.bool_

    # type groups
    IntTypes = (Int8, Int16, Int32, Int64, UInt8, UInt16, UInt32, UInt64)
    FloatTypes = (Float, Double)

    @classmethod
    def get_dtype(cls, value):
        if isinstance(value, BOOLS):
            return cls.Bool
        elif isinstance(value, Integral):
            return cls.Int64
        elif isinstance(value, Real):
            return cls.Double
        elif isinstance(value, string_types):
            return cls.String
        else:
            raise ValueError("Unknown type for value {}".format(value))

    @classmethod
    def is_numeric_dtype(cls, dtype):
        return dtype in cls.IntTypes + cls.FloatTypes
