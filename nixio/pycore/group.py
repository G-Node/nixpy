# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

from ..group import GroupMixin
from .entity_with_sources import EntityWithSources
from .data_array import DataArray
from .tag import Tag
from .multi_tag import MultiTag


class Group(EntityWithSources, GroupMixin):

    def __init__(self, h5group):
        super(Group, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Group, cls)._create_new(parent, name, type_)
        return newentity

    # DataArray
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
        return len(self._h5group.open_group("data_arrays"))

    def _add_data_array_by_id(self, id_or_name):
        data_arrays = self._h5group.open_group("data_arrays")
        data_arrays.add_by_id(id_or_name)

    def _has_data_array_by_id(self, id_or_name):
        data_arrays = self._h5group.open_group("data_arrays")
        return data_arrays.has_by_id(id_or_name)

    # MultiTag
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
        return len(self._h5group.open_group("multi_tags"))

    def _add_multi_tag_by_id(self, id_or_name):
        multi_tags = self._h5group.open_group("multi_tags")
        multi_tags.add_by_id(id_or_name)

    def _has_multi_tag_by_id(self, id_or_name):
        multi_tags = self._h5group.open_group("multi_tags")
        return multi_tags.has_by_id(id_or_name)

    # Tag
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
        return len(self._h5group.open_group("tags"))

    def _add_tag_by_id(self, id_or_name):
        tags = self._h5group.open_group("tags")
        tags.add_by_id(id_or_name)

    def _has_tag_by_id(self, id_or_name):
        tags = self._h5group.open_group("tags")
        return tags.has_by_id(id_or_name)

