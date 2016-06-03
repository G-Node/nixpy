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

    def __init__(self, h5group):
        super(Group, self).__init__(h5group)
        # TODO: Validate link containers

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Group, cls)._create_new(parent, name, type_)
        newentity._h5group.open_group("data_arrays")
        newentity._h5group.open_group("tags")
        newentity._h5group.open_group("multi_tags")
        return newentity

    # DataArray
    def _get_data_array_by_id(self, id_or_name):
        return DataArray(util.id_or_name_getter(self._h5group["data_arrays"],
                                                id_or_name))

    def _get_data_array_by_pos(self, pos):
        return DataArray(util.pos_getter(self._h5group["data_arrays"], pos))

    def _delete_data_array_by_id(self, id_or_name):
        util.deleter(self._h5group["data_arrays"], id_or_name)

    def _data_array_count(self):
        return len(self._h5group["data_arrays"])

    # MultiTag
    def _get_multi_tag_by_id(self, id_or_name):
        return MultiTag(util.id_or_name_getter(self._h5group["multi_tags"],
                                               id_or_name))

    def _get_multi_tag_by_pos(self, pos):
        return MultiTag(util.pos_getter(self._h5group["multi_tags"], pos))

    def _delete_multi_tag_by_id(self, id_or_name):
        util.deleter(self._h5group["multi_tags"], id_or_name)

    def _multi_tag_count(self):
        return len(self._h5group["multi_tags"])

    # Tag
    def _get_tag_by_id(self, id_or_name):
        return Tag(util.id_or_name_getter(self._h5group["tags"], id_or_name))

    def _get_tag_by_pos(self, pos):
        return Tag(util.pos_getter(self._h5group["tags"], pos))

    def _delete_tag_by_id(self, id_or_name):
        util.deleter(self._h5group["tags"], id_or_name)

    def _tag_count(self):
        return len(self._h5group["tags"])

util.create_link_methods(Group, DataArray, "data_array")
util.create_link_methods(Group, Tag, "tag")
util.create_link_methods(Group, MultiTag, "multi_tag")
