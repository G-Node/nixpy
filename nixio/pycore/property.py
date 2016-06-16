# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import Entity
from ..property import PropertyMixin
from .util import util


class Property(Entity, PropertyMixin):

    def __init__(self, h5group):
        super(Property, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, name, dtype):
        newentity = super(Property, cls)._create_new(parent)
        newentity._h5group.set_attr("name", name)
        # TODO: Create dataset and use it for storing all property info
        # TODO: Does a property also create a Group object in the file?
        # newentity._h5group.create_dataset()
        return newentity

    @property
    def name(self):
        return self._h5group.get_attr("name")

    @property
    def definition(self):
        return self._h5group.get_attr("definition")

    @definition.setter
    def definition(self, d):
        util.check_attr_type(d, str)
        self._h5group.set_attr("definition", d)

    @property
    def mapping(self):
        return self._h5group.get_attr("mapping")

    @mapping.setter
    def mapping(self, mapping):
        util.check_attr_type(mapping, str)
        self._h5group.set_attr("mapping", mapping)

    @property
    def unit(self):
        return self._h5group.get_attr("unit")

    @unit.setter
    def unit(self, u):
        util.check_attr_type(u, str)
        self._h5group.set_attr("unit", u)

    def delete_values(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass
