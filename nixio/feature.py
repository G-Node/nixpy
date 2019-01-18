# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from .entity import Entity
from .data_array import DataArray
from .util import util


class Feature(Entity):

    def __init__(self, nixparent, h5group):
        super(Feature, self).__init__(nixparent, h5group)

    @classmethod
    def _create_new(cls, nixparent, h5parent, data, link_type):
        newentity = super(Feature, cls)._create_new(nixparent, h5parent)
        newentity.link_type = link_type
        newentity.data = data
        return newentity

    @property
    def id(self):
        return self._h5group.get_attr("entity_id")

    @property
    def link_type(self):
        return util.link_type_from_string(self._h5group.get_attr("link_type"))

    @link_type.setter
    def link_type(self, lt):
        self._h5group.set_attr("link_type", util.link_type_to_string(lt))

    @property
    def data(self):
        if "data" not in self._h5group:
            raise RuntimeError("Feature.data: DataArray not found!")
        return DataArray(self._parent._parent,
                         self._h5group.open_group("data"))

    @data.setter
    def data(self, da):
        if da is None:
            raise TypeError("Feature.data cannot be None.")
        parblock = self._parent._parent
        if da not in parblock.data_arrays:
            raise RuntimeError("Feature.data: DataArray not found in Block!")
        if "data" in self._h5group:
            del self._h5group["data"]
        self._h5group.create_link(da, "data")
        self.force_updated_at()
