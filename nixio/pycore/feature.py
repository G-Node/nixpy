# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import Entity
from .data_array import DataArray
from ..link_type import LinkType


class Feature(Entity):

    def __init__(self, h5group):
        super(Feature, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, data, link_type):
        newentity = super(Feature, cls)._create_new(parent)
        newentity.link_type = link_type
        newentity.data = data
        return newentity

    @property
    def id(self):
        return self._h5group.get_attr("entity_id")

    @property
    def link_type(self):
        return self._h5group.get_attr("link_type")

    @link_type.setter
    def link_type(self, lt):
        if lt not in (LinkType.Indexed, LinkType.Tagged, LinkType.Untagged):
            raise ValueError("Invalid link type.")
        self._h5group.set_attr("link_type", lt)

    @property
    def data(self):
        return DataArray(self._h5group.open_group("data"))

    @data.setter
    def data(self, da):
        if da is None:
            raise TypeError("Feature.data cannot be None.")
        parblock = self._h5group.root
        if da not in parblock.data_arrays:
            raise RuntimeError("Feature.data: DataArray not found in Block!")
        if "data" in self._h5group:
            del self._h5group["data"]
        self._h5group.create_link(da, "data")
        self.force_updated_at()
