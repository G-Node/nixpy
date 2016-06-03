# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from time import time
from . import util


class Entity(object):

    def __init__(self, h5obj):
        util.check_entity_id(h5obj.get_attr("id"))
        self._h5obj = h5obj

    @classmethod
    def _create_new(cls, h5obj):
        h5obj.set_attr("id", util.create_id())
        h5obj.set_attr("created_at", int(time()))
        h5obj.set_attr("updated_at", int(time()))
        return cls(h5obj)

# util.create_h5props(Entity, ("created_at", "updated_at", "id"))


class NamedEntity(object):

    def __init__(self, h5obj):
        self._h5obj = h5obj
        # TODO: Validate object
        try:
            util.check_entity_name_and_type(h5obj.get_attr("name"),
                                            h5obj.get_attr("type"))
            util.check_entity_id(h5obj.get_attr("id"))
        except ValueError:
            ValueError("Invalid NIX object found in file.")

    @classmethod
    def _create_new(cls, parent, name, type_):
        util.check_entity_name_and_type(name, type_)
        h5obj = parent.create_group(name)
        h5obj.set_attr("name", name)
        h5obj.set_attr("type", type_)
        h5obj.set_attr("id", util.create_id())
        h5obj.set_attr("created_at", int(time()))
        h5obj.set_attr("updated_at", int(time()))
        newentity = cls(h5obj)
        return newentity

    def force_created_at(self, t):
        # TODO: Check if convertible to date
        self.created_at = t

    def force_updated_at(self, t):
        # TODO: Check if convertible to date
        self.updated_at = t

    def __str__(self):
        return "{}: {{name = {}, type = {}, id = {}}}".format(
            type(self).__name__, self.name, self.type, self.id
        )

    def __repr__(self):
        return self.__str__()

# util.create_h5props(NamedEntity,
#                     ("name", "type", "definition", "id",
#                      "created_at", "updated_at"),
#                     (str, str, str, str, int, int))

