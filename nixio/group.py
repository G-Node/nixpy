# -*- coding: utf-8 -*-
# Copyright © 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import Entity
from .data_array import DataArray
from .tag import Tag
from .multi_tag import MultiTag
from .container import LinkContainer
from .source_link_container import SourceLinkContainer
from .section import Section


class Group(Entity):

    def __init__(self, nixparent, h5group):
        super(Group, self).__init__(nixparent, h5group)
        self._data_arrays = None
        self._tags = None
        self._multi_tags = None
        self._sources = None

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

    @property
    def sources(self):
        """
        A property containing all Sources referenced by the Group. Sources
        can be obtained by index or their id. Sources can be removed from the
        list, but removing a referenced Source will not remove it from the
        file. New Sources can be added using the append method of the list.
        This is a read only attribute.
        """
        if self._sources is None:
            self._sources = SourceLinkContainer(self)
        return self._sources

    # metadata
    @property
    def metadata(self):
        """

        Associated metadata of the entity. Sections attached to the entity via
        this attribute can provide additional annotations. This is an optional
        read-write property, and can be None if no metadata is available.

        :type: Section
        """
        if "metadata" in self._h5group:
            return Section(None, self._h5group.open_group("metadata"))
        else:
            return None

    @metadata.setter
    def metadata(self, sect):
        if not isinstance(sect, Section):
            raise TypeError("{} is not of type Section".format(sect))
        self._h5group.create_link(sect, "metadata")

    @metadata.deleter
    def metadata(self):
        if "metadata" in self._h5group:
            self._h5group.delete("metadata")
