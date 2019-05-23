# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import annotations
from . import util
from typing import AnyStr


class Entity(object):

    def __init__(self, nixparent, h5group) -> None:
        util.check_entity_id(h5group.get_attr("entity_id"))
        self._h5group = h5group
        self._parent = nixparent

    @classmethod
    def _create_new(cls, nixparent, h5parent, name=None, type_=None) -> Entity:
        if name and type_:
            util.check_entity_name_and_type(name, type_)
            id_ = util.create_id()
        else:
            name = util.create_id()
            id_ = name
        h5group = h5parent.open_group(name)
        h5group.set_attr("name", name)
        h5group.set_attr("type", type_)
        h5group.set_attr("entity_id", id_)
        newentity = cls(nixparent, h5group)
        newentity.force_created_at()
        newentity.force_updated_at()
        return newentity

    @property
    def id(self) -> AnyStr:
        """
        A property providing the ID of the Entity. The id is generated
        automatically, therefore the property is read-only.

        :rtype: str
        """
        return self._h5group.get_attr("entity_id")

    @property
    def created_at(self) -> int:
        """
        The creation time of the entity. This is a read-only property.
        Use `force_created_at` in order to change the creation time.

        :rtype: int
        """
        return util.str_to_time(self._h5group.get_attr("created_at"))

    def force_created_at(self, t=None) -> None:
        """
        Sets the creation time `created_at` to the given time
        (default: current time).

        :param t: The time to set.
        :type t: int
        """
        if t is None:
            t = util.now_int()
        else:
            util.check_attr_type(t, int)
        self._h5group.set_attr("created_at", util.time_to_str(t))

    @property
    def updated_at(self) -> int:
        """
        The time of the last update of the entity. This is a read-only
        property. Use `force_updated_at` in order to change the update
        time.

        :rtype: int
        """
        return util.str_to_time(self._h5group.get_attr("updated_at"))

    def force_updated_at(self, t=None) -> None:
        """
        Sets the update time `updated_at` to the given time.
        (default: current time)

        :param t: The time to set.
        :type t: int
        """
        if t is None:
            t = util.now_int()
        else:
            util.check_attr_type(t, int)
        self._h5group.set_attr("updated_at", util.time_to_str(t))

    @property
    def definition(self) -> AnyStr:
        """
        The definition of the entity. The definition can contain a textual
        description of the entity. This is an optional read-write
        property, and can be None if no definition is available.

        :type: str
        """
        return self._h5group.get_attr("definition")

    @definition.setter
    def definition(self, d) -> None:
        util.check_attr_type(d, str)
        self._h5group.set_attr("definition", d)
        par = self._parent
        while isinstance(par, Entity):
            par = par._parent
        if par.time_auto_update:
            self.force_updated_at()

    @property
    def name(self) -> AnyStr:
        """
        The name of an entity. The name serves as a human readable
        identifier. This is a read-only property; entities cannot be
        renamed.

        :type: str
        """
        return self._h5group.get_attr("name")

    @property
    def type(self) -> AnyStr:
        """
        The type of the entity. The type is used in order to add semantic
        meaning to the entity. This is a read-write property, but it can't
        be set to None.

        :type: str
        """
        return self._h5group.get_attr("type")

    @type.setter
    def type(self, t) -> None:
        if t is None:
            raise AttributeError("type can't be None")
        util.check_attr_type(t, str)
        self._h5group.set_attr("type", t)
        par = self._parent
        while isinstance(par, Entity):
            par = par._parent
        if par.time_auto_update:
            self.force_updated_at()

    def __eq__(self, other):
        """
        Two Entities are considered equal when they have the same id.
        """
        if hasattr(other, "id"):
            return self.id == other.id
        return False

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class,
        implemented or escaped
        """
        return hash(self.id)

    def __str__(self):
        return "{}: {{name = {}, type = {}}}".format(
            type(self).__name__, self.name, self.type
        )

    def __repr__(self):
        return self.__str__()
