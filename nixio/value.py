# Copyright (c) 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import numpy as np

integers = (int,)
try:
    integers += (long,)
except NameError:
    pass

strings = (str, bytes)
try:
    strings += (basestring,)
except NameError:
    pass

valid_types = (bool, float, integers, strings)


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
        if isinstance(value, bool):
            return cls.Bool
        elif isinstance(value, integers):
            return cls.Int64
        elif isinstance(value, float):
            return cls.Float
        elif isinstance(value, strings):
            return cls.String

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
        self.reference = ""
        self.filename = ""
        self.encoder = ""
        self.checksum = ""
        self.uncertainty = 0
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

    def __hash__(self):
        """
        Overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class,
        implemented or escaped
        """
        return hash(self.id)
