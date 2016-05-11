# Copyright (c) 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import numpy as np
try:
    from nixio.core import CValue, CDataType
except ImportError:
    CValue = None
    CDataType = None

try:
    integers = (int, long)
except NameError:
    integers = (int,)
try:
    strings = (str, bytes, basestring)
except NameError:
    strings = (str, bytes)

valid_types = (bool, float, *integers, *strings)


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


class Value(object):

    def __init__(self, value):
        # super(Value, self).__init__(*args, **kwargs)
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

    def to_cvalue(self):
        if CValue:
            cvalue = CValue(self.value)
            return cvalue
        else:
            raise RuntimeError("HDF5 backend is not available.")

    @staticmethod
    def dtype_from_c(cdtype):
        if cdtype is CDataType.UInt8:
            dtype = DataType.UInt8
        elif cdtype is CDataType.UInt16:
            dtype = DataType.UInt16
        elif cdtype is CDataType.UInt32:
            dtype = DataType.UInt32
        elif cdtype is CDataType.UInt64:
            dtype = DataType.UInt64
        elif cdtype is CDataType.Int8:
            dtype = DataType.Int8
        elif cdtype is CDataType.Int16:
            dtype = DataType.Int16
        elif cdtype is CDataType.Int32:
            dtype = DataType.Int32
        elif cdtype is CDataType.Int64:
            dtype = DataType.Int64
        elif cdtype is CDataType.Float:
            dtype = DataType.Float
        elif cdtype is CDataType.Double:
            dtype = DataType.Double
        elif cdtype is CDataType.String:
            dtype = DataType.String
        elif cdtype is CDataType.Bool:
            dtype = DataType.Bool
        else:
            raise TypeError("Unknown data type ({}).".format(cdtype))
        return dtype

    @staticmethod
    def dtype_to_c(dtype):
        if dtype in (DataType.UInt8, DataType.UInt16, CDataType.UInt16,
                     DataType.UInt32, DataType.UInt64):
            cdtype = CDataType.UInt64
        elif dtype in (DataType.Int8, DataType.Int16, CDataType.Int16,
                       DataType.Int32, DataType.Int64):
            cdtype = CDataType.Int64
        elif dtype in (DataType.Float, CDataType.Double):
            cdtype = CDataType.Double
        elif dtype is DataType.String:
            cdtype = CDataType.String
        elif dtype is DataType.Bool:
            cdtype = CDataType.Bool
        else:
            raise TypeError("Unknown data type ({}).".format(dtype))
        return cdtype

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
