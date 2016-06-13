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

    def __init__(self, h5group):
        super(Block, self).__init__(h5group)
        # TODO: Validation for containers

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Block, cls)._create_new(parent, name, type_)
        return newentity

    # DataArray
    def _create_data_array(self, name, type_, data_type, shape):
        util.check_entity_name_and_type(name, type_)
        data_arrays = self._h5group.open_group("data_arrays", True)
        if name in data_arrays:
            raise exceptions.DuplicateName("create_data_array")
        da = DataArray._create_new(data_arrays, name, type_, data_type, shape)
        return da

    def _get_data_array_by_id(self, id_or_name):
        data_arrays = self._h5group.open_group("data_arrays")
        return DataArray(data_arrays.get_by_id_or_name(id_or_name))

    def _get_data_array_by_pos(self, pos):
        data_arrays = self._h5group.open_group("data_arrays")
        return DataArray(data_arrays.get_by_pos(pos))

    def _delete_data_array_by_id(self, id_or_name):
        data_arrays = self._h5group.open_group("data_arrays")
        data_arrays.delete(id_or_name)

    def _data_array_count(self):
        data_arrays = self._h5group.open_group("data_arrays")
        return len(data_arrays)

    # MultiTag
    def create_multi_tag(self, name, type_, positions):
        util.check_entity_name_and_type(name, type_)
        util.check_entity_input(positions)
        if not isinstance(positions, DataArray):
            raise TypeError("DataArray expected for 'positions'")
        multi_tags = self._h5group.open_group("multi_tags", True)
        if name in multi_tags:
            raise exceptions.DuplicateName("create_multi_tag")
        mtag = MultiTag._create_new(multi_tags, name, type_, positions)
        return mtag

    def _get_multi_tag_by_id(self, id_or_name):
        multi_tags = self._h5group.open_group("multi_tags")
        return MultiTag(multi_tags.get_by_id_or_name(id_or_name))

    def _get_multi_tag_by_pos(self, pos):
        multi_tags = self._h5group.open_group("multi_tags")
        return MultiTag(multi_tags.get_by_pos(pos))

    def _delete_multi_tag_by_id(self, id_or_name):
        multi_tags = self._h5group.open_group("multi_tags")
        multi_tags.delete(id_or_name)

    def _multi_tag_count(self):
        multi_tags = self._h5group.open_group("multi_tags")
        return len(multi_tags)

    # Tag
    def create_tag(self, name, type_, position):
        util.check_entity_name_and_type(name, type_)
        tags = self._h5group.open_group("tags")
        if name in tags:
            raise exceptions.DuplicateName("create_tag")
        tag = Tag._create_new(tags, name, type_, position)
        return tag

    def _get_tag_by_id(self, id_or_name):
        tags = self._h5group.open_group("tags")
        return Tag(tags.get_by_id_or_name(id_or_name))

    def _get_tag_by_pos(self, pos):
        tags = self._h5group.open_group("tags")
        return Tag(tags.get_by_pos(pos))

    def _delete_tag_by_id(self, id_or_name):
        tags = self._h5group.open_group("tags")
        tags.delete(id_or_name)

    def _tag_count(self):
        tags = self._h5group.open_group("tags")
        return len(tags)

    # Source
    def create_source(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        sources = self._h5group.open_group("sources")
        if name in sources:
            raise exceptions.DuplicateName("create_source")
        src = Source._create_new(sources, name, type_)
        return src

    def _get_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        return Source(sources.get_by_id_or_name(id_or_name))

    def _get_source_by_pos(self, pos):
        sources = self._h5group.open_group("sources")
        return Source(sources.get_by_pos(pos))

    def _delete_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        sources.delete(id_or_name)

    def _source_count(self):
        sources = self._h5group.open_group("sources")
        return len(sources)

    # Group
    def create_group(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        groups = self._h5group.open_group("groups")
        if name in groups:
            raise exceptions.DuplicateName("open_group")
        grp = Group._create_new(groups, name, type_)
        return grp

    def _get_group_by_id(self, id_or_name):
        groups = self._h5group.open_group("groups")
        return Group(groups.get_by_id_or_name(id_or_name))

    def _get_group_by_pos(self, pos):
        groups = self._h5group.open_group("groups")
        return Group(groups.get_by_pos(pos))

    def _delete_group_by_id(self, id_or_name):
        groups = self._h5group.open_group("groups")
        groups.delete(id_or_name)

    def _group_count(self):
        groups = self._h5group.open_group("groups")
        return len(groups)

