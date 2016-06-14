# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import Entity
from .data_array import DataArray


class LinkType(object):
    Tagged = "tagged"
    Untagged = "untagged"
    Indexed = "indexed"


class Feature(Entity):

    def __init__(self):
        super(Feature, self).__init__()

    @classmethod
    def _create_new(cls, parent, data, link_type):
        newentity = super(Feature, cls)._create_new(parent)
        newentity._h5group.set_attr("link_type", link_type)
        datagroup = newentity._h5group.create_link(data, "data")
        return newentity

    @property
    def id(self):
        return self._h5group.get_attr("id")

    @property
    def link_type(self):
        return self._h5group.get_attr("link_type")

    @property
    def data(self):
        return DataArray(self._h5group.open_group("data"))
