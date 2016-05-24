# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from time import time
from . import util
from . import exceptions


class Entity(object):

    def __init__(self, h5obj):
        util.check_entity_id(h5obj.attrs.get("id"))
        self._h5obj = h5obj

    @classmethod
    def _create_new(cls, h5obj):
        h5obj.attrs["id"] = util.create_id()
        h5obj.attrs["created_at"] = int(time())
        h5obj.attrs["updated_at"] = int(time())
        return cls(h5obj)

util.create_h5props(Entity, ("created_at", "updated_at", "id"))


class NamedEntity(object):

    def __init__(self, h5obj):
        self._h5obj = h5obj
        # TODO: Validate object
        try:
            util.check_entity_name_and_type(h5obj.attrs.get("name"),
                                            h5obj.attrs.get("type"))
            util.check_entity_id(h5obj.attrs.get("id"))
        except ValueError:
            ValueError("Invalid NIX object found in file.")

    @classmethod
    def _create_new(cls, parent, name, type_):
        util.check_entity_name_and_type(name, type_)
        h5obj = parent.create_group(name)
        h5obj.attrs["name"] = name
        h5obj.attrs["type"] = type_
        h5obj.attrs["id"] = util.create_id()
        h5obj.attrs["created_at"] = int(time())
        h5obj.attrs["updated_at"] = int(time())
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

util.create_h5props(NamedEntity, ("name", "type", "definition",
                                  "id", "created_at", "updated_at"))


class EntityWithMetadata(NamedEntity):

    def __init__(self, h5obj):
        super(EntityWithMetadata, self).__init__(h5obj)
        # TODO: Additional validation for metadata

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(EntityWithMetadata, cls)._create_new(parent,
                                                               name, type_)
        newentity.metadata = None  # TODO: Metadata section
        return newentity


class EntityWithSources(EntityWithMetadata):

    def __init__(self, h5obj):
        super(EntityWithSources, self).__init__(h5obj)

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(EntityWithSources, cls)._create_new(parent,
                                                              name, type_)
        return newentity
