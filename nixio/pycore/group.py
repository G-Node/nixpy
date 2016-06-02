# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from ..group import GroupMixin
from .entity_with_sources import EntityWithSources
from . import util
from .data_array import DataArray
from .tag import Tag
from .multi_tag import MultiTag


class Group(EntityWithSources, GroupMixin):

    def __init__(self, h5obj):
        super(Group, self).__init__(h5obj)
        # TODO: Validate link containers

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Group, cls)._create_new(parent, name, type_)
        newentity._h5obj.create_group("data_arrays")
        newentity._h5obj.create_group("tags")
        newentity._h5obj.create_group("multi_tags")
        return newentity


util.create_container_methods(Group, DataArray, "data_array")
util.create_container_methods(Group, Tag, "tag")
util.create_container_methods(Group, MultiTag, "multi_tag")

util.create_link_methods(Group, DataArray, "data_array")
util.create_link_methods(Group, Tag, "tag")
util.create_link_methods(Group, MultiTag, "multi_tag")
