# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

from .entity_with_sources import EntityWithSources
from .data_array import DataArray
from .tag import Tag
from .multi_tag import MultiTag
from .container import LinkContainer


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
            self._data_arrays = LinkContainer("data_arrays", self, DataArray,
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
            self._tags = LinkContainer("tags", self, Tag, self._parent.tags)
        return self._tags

    @property
    def multi_tags(self):
        """
        A property containing all MultiTags referenced by the group. MultiTags
        can be obtained by index or their id. MultiTags can be removed from the
        list, removing a referenced MultiTag will not remove it from the file.
        New MultiTags can be added using the append method of the list.
        This is a read only attribute.
        """
        if self._multi_tags is None:
            self._multi_tags = LinkContainer("multi_tags", self, MultiTag,
                                             self._parent.multi_tags)
        return self._multi_tags
