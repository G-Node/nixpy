# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import
from .entity_with_metadata import EntityWithMetadata
from . import util
from . import exceptions
from . import Group, DataArray, MultiTag, Tag, Source


class Block(EntityWithMetadata):

    def __init__(self, h5obj):
        super(Block, self).__init__(h5obj)
        # TODO: Validation for containers

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Block, cls)._create_new(parent, name, type_)
        newentity._h5obj.create_group("groups")
        newentity._h5obj.create_group("data_arrays")
        newentity._h5obj.create_group("tags")
        newentity._h5obj.create_group("multi_tags")
        newentity._h5obj.create_group("sources")
        return newentity

    # DataArray
    def _create_data_array(self, name, type_, data_type, shape):
        util.check_entity_name_and_type(name, type_)
        data_arrays = self._h5obj["data_arrays"]
        if name in data_arrays:
            raise exceptions.DuplicateName("create_data_array")
        da = DataArray._create_new(data_arrays, name, type_, data_type, shape)
        return da

    # MultiTag
    def create_multi_tag(self, name, type_, positions):
        util.check_entity_name_and_type(name, type_)
        util.check_entity_input(positions)
        if not isinstance(positions, DataArray):
            raise TypeError("DataArray expected for 'positions'")
        multi_tags = self._h5obj["multi_tags"]
        if name in multi_tags:
            raise exceptions.DuplicateName("create_multi_tag")
        mtag = MultiTag._create_new(multi_tags, name, type_, positions)
        return mtag

    # Tag
    def create_tag(self, name, type_, position):
        util.check_entity_name_and_type(name, type_)
        tags = self._h5obj["tags"]
        if name in tags:
            raise exceptions.DuplicateName("create_tag")
        tag = Tag._create_new(tags, name, type_, position)
        return tag

    # Source
    def create_source(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        sources = self._h5obj["sources"]
        if name in sources:
            raise exceptions.DuplicateName("create_source")
        src = Source._create_new(sources, name, type_)
        return src

    # Group
    def create_group(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        groups = self._h5obj["groups"]
        if name in groups:
            raise exceptions.DuplicateName("create_group")
        grp = Group._create_new(groups, name, type_)
        return grp


util.create_container_methods(Block, DataArray, "data_array")
util.create_container_methods(Block, Tag, "tag")
util.create_container_methods(Block, MultiTag, "multi_tag")
util.create_container_methods(Block, Group, "group")
util.create_container_methods(Block, Source, "source")
