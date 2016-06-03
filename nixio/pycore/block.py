# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import
from .entity_with_metadata import EntityWithMetadata
from ..block import BlockMixin
from . import util, exceptions, Group, DataArray, MultiTag, Tag, Source


class Block(EntityWithMetadata, BlockMixin):

    def __init__(self, h5obj):
        super(Block, self).__init__(h5obj)
        # TODO: Validation for containers

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Block, cls)._create_new(parent, name, type_)
        newentity._h5obj.create_group("groups")
        # newentity._h5obj.create_group("data_arrays")
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

    def _get_data_array_by_id(self, id_or_name):
        return DataArray(util.id_or_name_getter(self._h5obj["data_arrays"],
                                                id_or_name))

    def _get_data_array_by_pos(self, pos):
        return DataArray(util.pos_getter(self._h5obj["data_arrays"], pos))

    def _delete_data_array_by_id(self, id_or_name):
        util.deleter(self._h5obj["data_arrays"], id_or_name)

    def _data_array_count(self):
        return len(self._h5obj["data_arrays"])

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

    def _get_multi_tag_by_id(self, id_or_name):
        return MultiTag(util.id_or_name_getter(self._h5obj["multi_tags"],
                                                id_or_name))

    def _get_multi_tag_by_pos(self, pos):
        return MultiTag(util.pos_getter(self._h5obj["multi_tags"], pos))

    def _delete_multi_tag_by_id(self, id_or_name):
        util.deleter(self._h5obj["multi_tags"], id_or_name)

    def _multi_tag_count(self):
        return len(self._h5obj["multi_tags"])

    # Tag
    def create_tag(self, name, type_, position):
        util.check_entity_name_and_type(name, type_)
        tags = self._h5obj["tags"]
        if name in tags:
            raise exceptions.DuplicateName("create_tag")
        tag = Tag._create_new(tags, name, type_, position)
        return tag

    def _get_tag_by_id(self, id_or_name):
        return Tag(util.id_or_name_getter(self._h5obj["tags"], id_or_name))

    def _get_tag_by_pos(self, pos):
        return Tag(util.pos_getter(self._h5obj["tags"], pos))

    def _delete_tag_by_id(self, id_or_name):
        util.deleter(self._h5obj["tags"], id_or_name)

    def _tag_count(self):
        return len(self._h5obj["tags"])

    # Source
    def create_source(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        sources = self._h5obj["sources"]
        if name in sources:
            raise exceptions.DuplicateName("create_source")
        src = Source._create_new(sources, name, type_)
        return src

    def _get_source_by_id(self, id_or_name):
        return Source(util.id_or_name_getter(self._h5obj["sources"],
                                             id_or_name))

    def _get_source_by_pos(self, pos):
        return Source(util.pos_getter(self._h5obj["sources"], pos))

    def _delete_source_by_id(self, id_or_name):
        util.deleter(self._h5obj["sources"], id_or_name)

    def _source_count(self):
        return len(self._h5obj["sources"])

    # Group
    def create_group(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        groups = self._h5obj["groups"]
        if name in groups:
            raise exceptions.DuplicateName("create_group")
        grp = Group._create_new(groups, name, type_)
        return grp

    def _get_group_by_id(self, id_or_name):
        return Group(util.id_or_name_getter(self._h5obj["groups"], id_or_name))

    def _get_group_by_pos(self, pos):
        return Group(util.pos_getter(self._h5obj["groups"], pos))

    def _delete_group_by_id(self, id_or_name):
        util.deleter(self._h5obj["groups"], id_or_name)

    def _group_count(self):
        return len(self._h5obj["groups"])
