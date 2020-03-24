# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

try:
    from collections.abc import Sequence, Iterable
except ImportError:
    from collections import Sequence, Iterable
from enum import Enum
from numbers import Number
from six import string_types, ensure_str, ensure_text
import numpy as np

from .datatype import DataType
from .entity import Entity
from . import util


class OdmlType(Enum):
    """
    OdmlType provides all types currently supported by the odML
    data format. It provides additional information about the
    nature of the values of an odML Property.
    """
    Boolean = 'boolean'
    Int = 'int'
    Float = 'float'
    String = 'string'
    Text = 'text'
    URL = 'url'
    Person = 'person'
    Datetime = 'datetime'
    Date = 'date'
    Time = 'time'

    def __str__(self):
        return self.value

    def compatible(self, value):
        """
        compatible returns True or False depending on whether a
        passed value can be mapped to an OdmlType or not.

        :param value: Any single value
        :return: Boolean
        """
        if (self in (self.String, self.Text, self.URL, self.Person) and
                DataType.get_dtype(value) == DataType.String):
            return True
        elif (self == self.Boolean and
              DataType.get_dtype(value) == DataType.Bool):
            return True
        elif (self == self.Float and
              DataType.get_dtype(value) == DataType.Float):
            return True
        elif self == self.Int and DataType.get_dtype(value) == DataType.Int64:
            return True
        elif (self in (self.Time, self.Date, self.Datetime) and
              DataType.get_dtype(value) == DataType.String):
            # This might need some extra work, treating as String for now, but
            # keeping it separated from other String values.
            return True

        return False

    @classmethod
    def get_odml_type(cls, dtype):
        """
        get_odml_type returns the appropriate OdmlType
        for a handed in nix value DataType.

        :param dtype: nix DataType
        :return: OdmlType
        """

        if dtype == DataType.Float:
            return cls.Float
        elif dtype == DataType.Int64:
            return cls.Int
        elif dtype == DataType.String:
            return cls.String
        elif dtype == DataType.Bool:
            return cls.Boolean

        raise TypeError("No available OdmlType for type '%s'" % dtype)


class Property(Entity):
    """An odML Property"""
    def __init__(self, nixparent, h5dataset):
        super(Property, self).__init__(nixparent, h5dataset)
        self._h5dataset = self._h5group

    @classmethod
    def _create_new(cls, nixparent, h5parent, name,
                    dtype, shape=None, oid=None):
        if shape is None or shape[0] == 0:
            shape = (8, )
        util.check_entity_name(name)
        dtype = cls._make_h5_dtype(dtype)

        h5dataset = h5parent.create_dataset(name, shape=shape, dtype=dtype)
        h5dataset.set_attr("name", name)

        if not util.is_uuid(oid):
            oid = util.create_id()

        h5dataset.set_attr("entity_id", oid)

        newentity = cls(nixparent, h5dataset)
        newentity.force_created_at()
        newentity.force_updated_at()

        return newentity

    @property
    def name(self):
        return self._h5dataset.get_attr("name")

    @property
    def definition(self):
        return self._h5dataset.get_attr("definition")

    @definition.setter
    def definition(self, d):
        util.check_attr_type(d, str)
        self._h5dataset.set_attr("definition", d)

    @property
    def unit(self):
        return self._h5dataset.get_attr("unit")

    @unit.setter
    def unit(self, new):
        if new:
            new = util.units.sanitizer(new)

        if new == "":
            new = None

        util.check_attr_type(new, str)
        self._h5dataset.set_attr("unit", new)

    @property
    def uncertainty(self):
        dataset = self._h5dataset
        filever = tuple(dataset._parent.file.attrs["version"])
        if filever < (1, 1, 1):
            val = self._h5dataset.dataset[:]
            v = val[0]["uncertainty"]
            return v
        return self._h5dataset.get_attr("uncertainty")

    @uncertainty.setter
    def uncertainty(self, uncertainty):
        util.check_attr_type(uncertainty, Number)
        uncertainty = float(uncertainty) if uncertainty is not None else None
        self._h5dataset.set_attr("uncertainty", uncertainty)

    @property
    def reference(self):
        dataset = self._h5dataset
        filever = tuple(dataset._parent.file.attrs["version"])
        if filever < (1, 1, 1):
            val = self._h5dataset.dataset[:]
            v = val[0]["reference"]
            return v
        return self._h5dataset.get_attr("reference")

    @reference.setter
    def reference(self, ref):
        util.check_attr_type(ref, str)
        self._h5dataset.set_attr("reference", ref)

    @property
    def dependency(self):
        return self._h5dataset.get_attr("dependency")

    @dependency.setter
    def dependency(self, dep):
        util.check_attr_type(dep, str)
        self._h5dataset.set_attr("dependency", dep)

    @property
    def dependency_value(self):
        return self._h5dataset.get_attr("dependency_value")

    @dependency_value.setter
    def dependency_value(self, depval):
        util.check_attr_type(depval, str)
        self._h5dataset.set_attr("dependency_value", depval)

    @property
    def value_origin(self):
        return self._h5dataset.get_attr("value_origin")

    @value_origin.setter
    def value_origin(self, origin):
        util.check_attr_type(origin, str)
        self._h5dataset.set_attr("value_origin", origin)

    @property
    def odml_type(self):
        otype = self._h5dataset.get_attr("odml_type")
        if not otype:
            return None

        return OdmlType(otype)

    @odml_type.setter
    def odml_type(self, new_type):
        """
        odml_type can only be set if the handed in new type is a valid
        OdmlType and if it is compatible with the value data type of
        the property.

        :param new_type: OdmlType
        """
        if not isinstance(new_type, OdmlType):
            raise TypeError("'{}' is not a valid odml_type.".format(new_type))

        if not new_type.compatible(self.values[0]):
            raise TypeError("Type '{}' is incompatible "
                            "with property values".format(new_type))

        self._h5dataset.set_attr("odml_type", str(new_type))

    def _read_old_values(self):
        val = self._h5dataset.dataset[:]
        val_tu = tuple()
        for v in val:
            v = v["value"]
            val_tu += (v,)
        return val_tu

    @property
    def values(self):
        dataset = self._h5dataset
        filever = tuple(dataset._parent.file.attrs["version"])
        if filever < (1, 1, 1):
            v = self._read_old_values()
            return v
        if not sum(dataset.shape):
            return tuple()

        data = dataset.read_data()

        def data_to_value(dat):
            if isinstance(dat, bytes):
                dat = ensure_str(dat)  # py2compat
            return dat

        values = tuple(map(data_to_value, data))

        return values

    @values.setter
    def values(self, vals):
        """
        Set the value of the property discarding any previous information.

        :param vals: a single value or list of values.
        """
        # Make sure boolean value 'False' gets through as well...
        if vals is None or (isinstance(vals, (Sequence, Iterable)) and
                            not len(vals)):
            self.delete_values()
            return

        if not isinstance(vals, (Sequence, Iterable)) \
                or isinstance(vals, string_types):
            vals = [vals]

        # Make sure all values are of the same data type
        vtype = self._check_new_value_types(vals)
        if vtype == DataType.String:
            vals = [ensure_text(v) for v in vals]  # py2compat
        self._h5dataset.shape = np.shape(vals)
        data = np.array(vals, dtype=vtype)
        self._h5dataset.write_data(data)

    def extend_values(self, data):
        """
        Extends values to existing data.
        Suitable when new data is nested or original data is long.
        """
        vtype = self._check_new_value_types(data)

        arr = np.array(data, dtype=vtype).flatten('C')
        ds = self._h5dataset
        src_len = len(self.values)
        dlen = len(arr)
        ds.shape = (src_len+dlen,)
        ds.write_data(arr, sl=np.s_[src_len: src_len+dlen])

    def _check_new_value_types(self, data):
        if (isinstance(data, (Sequence, Iterable)) and
                not isinstance(data, string_types)):
            single_val = data[0]
        else:
            single_val = data
            data = [data]

        def check_prop_consistent(vtype):
            # Check if the new data has the same type as the existing property
            # data
            if vtype != self.data_type:
                raise TypeError("New data type '{}' is inconsistent with the "
                                "Property's data type '{}'".format(
                                    vtype, self.data_type))

        def check_new_data_consistent(vtype):
            # Check if each value in the new data has the same type
            for val in data:
                if DataType.get_dtype(val) != vtype:
                    raise TypeError("Array contains inconsistent values. "
                                    "Only values of type '{}' can be "
                                    "assigned".format(vtype))

        if hasattr(data, "dtype"):
            # numpy array: no need to scan values, arrays are consistent but
            # check for 1D
            vtype = data.dtype
            check_prop_consistent(vtype)
        else:
            # Will raise an error, if the data type of the first value is not
            # valid
            vtype = DataType.get_dtype(single_val)
            check_prop_consistent(vtype)
            check_new_data_consistent(vtype)

        return vtype

    @property
    def data_type(self):
        dtype = self._h5dataset.dtype

        if dtype == util.vlen_str_dtype:
            return DataType.String

        return dtype

    def delete_values(self):
        self._h5dataset.shape = (0,)

    @staticmethod
    def _make_h5_dtype(valued_type):
        str_ = util.vlen_str_dtype

        if valued_type == DataType.String:
            valued_type = str_

        return valued_type

    def __str__(self):
        return "{}: {{name = {}}}".format(
            type(self).__name__, self.name
        )

    def __repr__(self):
        return self.__str__()

    def pprint(self, indent=2, max_length=80, current_depth=-1):
        """
        Pretty print method. Method is called in Section.pprint()
        """
        property_spaces = ""
        prefix = ""
        if current_depth >= 0:
            property_spaces = " " * ((current_depth + 2) * indent)
            prefix = "|-"
        if self.unit is None:
            value_string = str(self.values)
        else:
            value_string = "{}{}".format(self.values, self.unit)
        p_len = len(property_spaces) + len(self.name) + len(value_string)
        if p_len >= max_length - 4:
            split_len = int((max_length - len(property_spaces)
                             + len(self.name) - len(prefix))/2)
            str1 = value_string[0: split_len]
            str2 = value_string[-split_len:]
            print(("{}{} {}: {} ... {}".format(property_spaces, prefix,
                                               self.name, str1, str2)))
        else:
            print(("{}{} {}: {}".format(property_spaces, prefix, self.name,
                                        value_string)))
