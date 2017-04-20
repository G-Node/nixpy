# -*- coding: utf-8 -*-
# Copyright © 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity_with_sources import EntityWithSources
from .data_array import DataArray
from .tag import Tag
from .multi_tag import MultiTag
from .container import LinkContainer

from . import util


class Group(EntityWithSources):

    def __init__(self, nixparent, h5group):
        super(Group, self).__init__(nixparent, h5group)
        self._data_arrays = None
        self._tags = None
        self._multi_tags = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_):
        newentity = super(Group, cls)._create_new(nixparent, h5parent,
                                                  name, type_)
        return newentity

    # DataArray
    def _get_data_array_by_id(self, id_or_name):
        data_arrays = self._h5group.open_group("data_arrays")
        if not util.is_uuid(id_or_name):
            id_or_name = self._parent.data_arrays[id_or_name].id
        # Using get_by_name - linked entries use id as name in backend
        return DataArray(self._parent, data_arrays.get_by_name(id_or_name))

    def _get_data_array_by_pos(self, pos):
        data_arrays = self._h5group.open_group("data_arrays")
        return DataArray(self._parent, data_arrays.get_by_pos(pos))

    def _delete_data_array_by_id(self, id_):
        data_arrays = self._h5group.open_group("data_arrays")
        data_arrays.delete(id_)

    def _data_array_count(self):
        return len(self._h5group.open_group("data_arrays"))

    def _add_data_array_by_id(self, id_or_name):
        if id_or_name not in self._parent.data_arrays:
            raise RuntimeError("Group._add_data_array_by_id: "
                               "DataArray not found in Block!")
        target = self._parent.data_arrays[id_or_name]
        data_arrays = self._h5group.open_group("data_arrays")
        data_arrays.create_link(target, target.id)

    def _has_data_array_by_id(self, id_or_name):
        data_arrays = self._h5group.open_group("data_arrays")
        return data_arrays.has_by_id(id_or_name)

    # MultiTag
    def _get_multi_tag_by_id(self, id_or_name):
        multi_tags = self._h5group.open_group("multi_tags")
        if not util.is_uuid(id_or_name):
            id_or_name = self._parent.multi_tags[id_or_name].id
        # Using get_by_name - linked entries use id as name in backend
        return MultiTag(self._parent, multi_tags.get_by_name(id_or_name))

    def _get_multi_tag_by_pos(self, pos):
        multi_tags = self._h5group.open_group("multi_tags")
        return MultiTag(self._parent, multi_tags.get_by_pos(pos))

    def _delete_multi_tag_by_id(self, id_):
        multi_tags = self._h5group.open_group("multi_tags")
        multi_tags.delete(id_)

    def _multi_tag_count(self):
        return len(self._h5group.open_group("multi_tags"))

    def _add_multi_tag_by_id(self, id_or_name):
        if id_or_name not in self._parent.multi_tags:
            raise RuntimeError("Group._add_multi_tag_by_id: "
                               "MultiTag not found in Block!")
        target = self._parent.multi_tags[id_or_name]
        multi_tags = self._h5group.open_group("multi_tags")
        multi_tags.create_link(target, target.id)

    def _has_multi_tag_by_id(self, id_or_name):
        multi_tags = self._h5group.open_group("multi_tags")
        return multi_tags.has_by_id(id_or_name)

    # Tag
    def _get_tag_by_id(self, id_or_name):
        tags = self._h5group.open_group("tags")
        if not util.is_uuid(id_or_name):
            id_or_name = self._parent.tags[id_or_name].id
        # Using get_by_name - linked entries use id as name in backend
        return Tag(self._parent, tags.get_by_name(id_or_name))

    def _get_tag_by_pos(self, pos):
        tags = self._h5group.open_group("tags")
        return Tag(self._parent, tags.get_by_pos(pos))

    def _delete_tag_by_id(self, id_):
        tags = self._h5group.open_group("tags")
        tags.delete(id_)

    def _tag_count(self):
        return len(self._h5group.open_group("tags"))

    def _add_tag_by_id(self, id_or_name):
        if id_or_name not in self._parent.tags:
            raise RuntimeError("Group._add_tag_by_id: "
                               "Tag not found in Block!")
        target = self._parent.tags[id_or_name]
        tags = self._h5group.open_group("tags")
        tags.create_link(target, target.id)

    def _has_tag_by_id(self, id_or_name):
        tags = self._h5group.open_group("tags")
        return tags.has_by_id(id_or_name)

    @property
    def data_arrays(self):
        """
        A property containing all data arrays referenced by the group.
        Referenced data arrays can be obtained by index or their id. References
        can be removed from the list, removing a referenced DataArray will not
        remove it from the file. New references can be added using the append
        method of the list.
        This is a read only attribute.
        """
        if self._data_arrays is None:
            self._data_arrays = LinkContainer("data_arrays", self,
                                              DataArray,
                                              self._parent.data_arrays)
        return self._data_arrays

    @property
    def tags(self):
        """
        A property containing all tags referenced by the group. Tags can be
        obtained by index or their id. Tags can be removed from the list,
        removing a referenced Tag will not remove it from the file.
        New Tags can be added using the append method of the list.
        This is a read only attribute.
        """
        if self._tags is None:
            self._tags = LinkContainer("tags", self, Tag,
                                       self._parent.tags)
        return self._tags

    @property
    def multi_tags(self):
        """
        A property containing all MultiTags referenced by the group. MultiTags
        can be obtained by index or their id. Tags can be removed from the
        list, removing a referenced MultiTag will not remove it from the file.
        New MultiTags can be added using the append method of the list.
        This is a read only attribute.
        """
        if self._multi_tags is None:
            self._multi_tags = LinkContainer("multi_tags", self,
                                             MultiTag, self._parent.multi_tags)
        return self._multi_tags
