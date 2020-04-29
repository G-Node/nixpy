# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from .data_array import DataArray
from .link_type import LinkType
from six import string_types
from .util import util


class Feature(object):

    def __init__(self, nixparent, h5group):
        util.check_entity_id(h5group.get_attr("entity_id"))
        self._h5group = h5group
        self._parent = nixparent

    @classmethod
    def create_new(cls, nixparent, h5parent, data, link_type):
        id_ = util.create_id()
        h5group = h5parent.open_group(id_)
        h5group.set_attr("entity_id", id_)
        newfeature = cls(nixparent, h5group)
        newfeature.link_type = link_type
        newfeature.data = data
        newfeature._h5group.set_attr("created_at",
                                     util.time_to_str(util.now_int()))
        newfeature._h5group.set_attr("updated_at",
                                     util.time_to_str(util.now_int()))

        return newfeature

    @property
    def id(self):
        return self._h5group.get_attr("entity_id")

    @property
    def link_type(self):
        return LinkType(self._h5group.get_attr("link_type"))

    @link_type.setter
    def link_type(self, lt):
        if isinstance(lt, string_types):
            lt = lt.lower()
        lt = LinkType(lt)
        self._h5group.set_attr("link_type", lt.value)
        if self._parent._parent._parent.time_auto_update:
            t = util.now_int()
            self._h5group.set_attr("updated_at", util.time_to_str(t))

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
        if self._parent._parent._parent.time_auto_update:
            t = util.now_int()
            self._h5group.set_attr("updated_at", util.time_to_str(t))

    @property
    def created_at(self):
        """
        The creation time of the entity. This is a read-only property.
        Use `force_created_at` in order to change the creation time.

        :rtype: int
        """
        return util.str_to_time(self._h5group.get_attr("created_at"))

    @property
    def updated_at(self):
        """
        The time of the last update of the entity. This is a read-only
        property. Use `force_updated_at` in order to change the update
        time.

        :rtype: int
        """
        return util.str_to_time(self._h5group.get_attr("updated_at"))

    def __eq__(self, other):
        """
        Two Entities are considered equal when they have the same id.
        """
        if hasattr(other, "id"):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class,
        implemented or escaped
        """
        return hash(self.id)

    def __str__(self):
        return "Feature: {{data = {}, link_type = {} }}".\
            format(self.data.name, self.link_type)

    def __repr__(self):
        return self.__str__()
