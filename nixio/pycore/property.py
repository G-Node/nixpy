# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

import numpy as np

from ..property import PropertyMixin
from .entity import Entity
from ..value import Value, DataType
from . import util


class Property(Entity, PropertyMixin):

    def __init__(self, nixparent, h5dataset):
        super(Property, self).__init__(nixparent, h5dataset)
        self._h5dataset = self._h5group

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, dtype):
        util.check_entity_name(name)
        dtype = cls._make_h5_dtype(dtype)
        h5dataset = h5parent.create_dataset(name, shape=(0,), dtype=dtype)
        h5dataset.set_attr("name", name)
        h5dataset.set_attr("entity_id", util.create_id())
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
    def mapping(self):
        return self._h5dataset.get_attr("mapping")

    @mapping.setter
    def mapping(self, mapping):
        util.check_attr_type(mapping, str)
        self._h5dataset.set_attr("mapping", mapping)

    @property
    def unit(self):
        return self._h5dataset.get_attr("unit")

    @unit.setter
    def unit(self, u):
        util.check_attr_type(u, str)
        self._h5dataset.set_attr("unit", u)

    @property
    def values(self):
        dataset = self._h5dataset
        if not sum(dataset.shape):
            return tuple()
        data = np.empty(dataset.shape, dtype=dataset.dtype)
        self._h5dataset.read_data(data)

        def data_to_value(d):
            vitem = d["value"]
            if isinstance(vitem, bytes):
                vitem = vitem.decode()
            v = Value(vitem)
            v.uncertainty = d["uncertainty"]
            v.reference = d["reference"]
            v.filename = d["filename"]
            v.encoder = d["encoder"]
            v.checksum = d["checksum"]
            return v

        values = tuple(map(data_to_value, data))
        return values

    @values.setter
    def values(self, values):
        if not len(values):
            self.delete_values()
            return

        for v in values:
            util.check_attr_type(v, Value)

        self._h5dataset.shape = np.shape(values)

        dtype = self._h5dataset.dtype
        data = np.array([], dtype=dtype)
        for v in values:
            d = np.array((v.value, v.uncertainty, v.reference,
                          v.filename, v.encoder, v.checksum),
                         dtype=dtype)
            data = np.append(data, d)

        self._h5dataset.write_data(data)

    @property
    def data_type(self):
        dt = self._h5dataset.dtype[0].type
        if dt == util.vlen_str_dtype:
            return DataType.String
        else:
            return dt

    def delete_values(self):
        self._h5dataset.shape = (0,)

    @staticmethod
    def _make_h5_dtype(valuedtype):
        str_ = util.vlen_str_dtype
        common = [("uncertainty", float),
                  ("reference", str_),
                  ("filename",  str_),
                  ("encoder",   str_),
                  ("checksum",  str_)]

        if valuedtype == DataType.String:
            valuedtype = str_

        return np.dtype([("value", valuedtype)] + common)

    def __str__(self):
        return "{}: {{name = {}}}".format(
            type(self).__name__, self.name
        )

    def __repr__(self):
        return self.__str__()
