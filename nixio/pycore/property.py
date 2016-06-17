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
from ..value import Value
from . import util


class Property(PropertyMixin):

    def __init__(self, h5dataset):
        self._h5dataset = h5dataset

    @classmethod
    def _create_new(cls, parent, name, dtype):
        util.check_entity_name(name)
        h5dataset = parent.create_dataset(name, shape=(0,), dtype=dtype)
        h5dataset.set_attr("name", name)
        h5dataset.set_attr("entity_id", util.create_id())
        h5dataset.set_attr("created_at", int(util.now_int()))
        h5dataset.set_attr("updated_at", int(util.now_int()))
        newentity = cls(h5dataset)
        return newentity

    @property
    def id(self):
        return self._h5dataset.get_attr("entity_id")

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

    def delete_values(self):
        self._h5dataset.shape = (0,)

    def __str__(self):
        return "{}: {{name = {}}}".format(
            type(self).__name__, self.name
        )

    def __repr__(self):
        return self.__str__()

