# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

from .pycore.entity_with_metadata import EntityWithMetadata
from .pycore.exceptions import exceptions
from .group import Group
from .pycore.data_array import DataArray
from .pycore.multi_tag import MultiTag
from .pycore.tag import Tag
from .source import Source
from .pycore import util

from .util import find as finders
from .util.proxy_list import ProxyList

from sys import maxsize as maxint
import numpy as np


class SourceProxyList(ProxyList):

    def __init__(self, obj):
        super(SourceProxyList, self).__init__(obj, "_source_count",
                                              "_get_source_by_id",
                                              "_get_source_by_pos",
                                              "_delete_source_by_id")


class DataArrayProxyList(ProxyList):

    def __init__(self, obj):
        super(DataArrayProxyList, self).__init__(obj, "_data_array_count",
                                                 "_get_data_array_by_id",
                                                 "_get_data_array_by_pos",
                                                 "_delete_data_array_by_id")


class MultiTagProxyList(ProxyList):

    def __init__(self, obj):
        super(MultiTagProxyList, self).__init__(obj, "_multi_tag_count",
                                                "_get_multi_tag_by_id",
                                                "_get_multi_tag_by_pos",
                                                "_delete_multi_tag_by_id")


class TagProxyList(ProxyList):

    def __init__(self, obj):
        super(TagProxyList, self).__init__(obj, "_tag_count", "_get_tag_by_id",
                                           "_get_tag_by_pos",
                                           "_delete_tag_by_id")


class GroupProxyList(ProxyList):

    def __init__(self, obj):
        super(GroupProxyList, self).__init__(obj, "_group_count",
                                             "_get_group_by_id",
                                             "_get_group_by_pos",
                                             "_delete_group_by_id")


class Block(EntityWithMetadata):

    def __init__(self, nixparent, h5group):
        super(Block, self).__init__(nixparent, h5group)
        # TODO: Validation for containers

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_):
        newentity = super(Block, cls)._create_new(nixparent, h5parent,
                                                  name, type_)
        return newentity

    # DataArray
    def _create_data_array(self, name, type_, data_type, shape):
        util.check_entity_name_and_type(name, type_)
        data_arrays = self._h5group.open_group("data_arrays")
        if name in data_arrays:
            raise exceptions.DuplicateName("create_data_array")
        da = DataArray._create_new(self, data_arrays, name, type_,
                                   data_type, shape)
        return da

    def _get_data_array_by_id(self, id_or_name):
        data_arrays = self._h5group.open_group("data_arrays")
        return DataArray(self, data_arrays.get_by_id_or_name(id_or_name))

    def _get_data_array_by_pos(self, pos):
        data_arrays = self._h5group.open_group("data_arrays")
        return DataArray(self, data_arrays.get_by_pos(pos))

    def _delete_data_array_by_id(self, id_):
        data_arrays = self._h5group.open_group("data_arrays")
        data_arrays.delete(id_)

    def _data_array_count(self):
        data_arrays = self._h5group.open_group("data_arrays")
        return len(data_arrays)

    # MultiTag
    def create_multi_tag(self, name, type_, positions):
        """
        Create a new multi tag for this block.

        :param name: The name of the tag to create.
        :type name: str
        :param type_: The type of tag.
        :type type_: str
        :param positions: A data array defining all positions of the tag.
        :type positions: DataArray

        :returns: The newly created tag.
        :rtype: MultiTag
        """
        util.check_entity_name_and_type(name, type_)
        util.check_entity_input(positions)
        if not isinstance(positions, DataArray):
            raise TypeError("DataArray expected for 'positions'")
        multi_tags = self._h5group.open_group("multi_tags")
        if name in multi_tags:
            raise exceptions.DuplicateName("create_multi_tag")
        mtag = MultiTag._create_new(self, multi_tags, name, type_, positions)
        return mtag

    def _get_multi_tag_by_id(self, id_or_name):
        multi_tags = self._h5group.open_group("multi_tags")
        return MultiTag(self, multi_tags.get_by_id_or_name(id_or_name))

    def _get_multi_tag_by_pos(self, pos):
        multi_tags = self._h5group.open_group("multi_tags")
        return MultiTag(self, multi_tags.get_by_pos(pos))

    def _delete_multi_tag_by_id(self, id_):
        multi_tags = self._h5group.open_group("multi_tags")
        multi_tags.delete(id_)

    def _multi_tag_count(self):
        multi_tags = self._h5group.open_group("multi_tags")
        return len(multi_tags)

    # Tag
    def create_tag(self, name, type_, position):
        """
        Create a new tag for this block.

        :param name: The name of the tag to create.
        :type name: str
        :param type_: The type of tag.
        :type type_: str
        :param position: Coordinates of the start position
                         in units of the respective data dimension.

        :returns: The newly created tag.
        :rtype: Tag
        """
        util.check_entity_name_and_type(name, type_)
        tags = self._h5group.open_group("tags")
        if name in tags:
            raise exceptions.DuplicateName("create_tag")
        tag = Tag._create_new(self, tags, name, type_, position)
        return tag

    def _get_tag_by_id(self, id_or_name):
        tags = self._h5group.open_group("tags")
        return Tag(self, tags.get_by_id_or_name(id_or_name))

    def _get_tag_by_pos(self, pos):
        tags = self._h5group.open_group("tags")
        return Tag(self, tags.get_by_pos(pos))

    def _delete_tag_by_id(self, id_):
        tags = self._h5group.open_group("tags")
        tags.delete(id_)

    def _tag_count(self):
        tags = self._h5group.open_group("tags")
        return len(tags)

    # Source
    def create_source(self, name, type_):
        """
        Create a new source on this block.

        :param name: The name of the source to create.
        :type name: str
        :param type_: The type of the source.
        :type type_: str

        :returns: The newly created source.
        :rtype: Source
        """
        util.check_entity_name_and_type(name, type_)
        sources = self._h5group.open_group("sources")
        if name in sources:
            raise exceptions.DuplicateName("create_source")
        src = Source._create_new(self, sources, name, type_)
        return src

    def _get_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        return Source(self, sources.get_by_id_or_name(id_or_name))

    def _get_source_by_pos(self, pos):
        sources = self._h5group.open_group("sources")
        return Source(self, sources.get_by_pos(pos))

    def _delete_source_by_id(self, id_):
        sources = self._h5group.open_group("sources")
        sources.delete(id_)

    def _source_count(self):
        sources = self._h5group.open_group("sources")
        return len(sources)

    # Group
    def create_group(self, name, type_):
        """
        Create a new group on this block.

        :param name: The name of the group to create.
        :type name: str
        :param type_: The type of the group.
        :type type_: str

        :returns: The newly created group.
        :rtype: Group
        """
        util.check_entity_name_and_type(name, type_)
        groups = self._h5group.open_group("groups")
        if name in groups:
            raise exceptions.DuplicateName("open_group")
        grp = Group._create_new(self, groups, name, type_)
        return grp

    def _get_group_by_id(self, id_or_name):
        groups = self._h5group.open_group("groups")
        return Group(self, groups.get_by_id_or_name(id_or_name))

    def _get_group_by_pos(self, pos):
        groups = self._h5group.open_group("groups")
        return Group(self, groups.get_by_pos(pos))

    def _delete_group_by_id(self, id_):
        groups = self._h5group.open_group("groups")
        groups.delete(id_)

    def _group_count(self):
        groups = self._h5group.open_group("groups")
        return len(groups)

    def create_data_array(self, name, array_type,
                          dtype=None, shape=None, data=None):
        """
        Create a new data array for this block. Either ``shape``
        or ``data`` must be given. If both are given their shape must agree.
        If ``dtype`` is not specified it will default to 64-bit floating
        points.

        :param name: The name of the data array to create.
        :type name: str
        :param array_type: The type of the data array.
        :type array_type: str
        :param dtype: Which data-type to use for storage
        :type dtype:  :class:`numpy.dtype`
        :param shape: Layout (dimensionality and extent)
        :type shape: tuple of int or long
        :param data: Data to write after storage has been created
        :type data: array-like data

        :returns: The newly created data array.
        :rtype: :class:`~nixio.DataArray`
        """

        if data is None:
            if shape is None:
                raise ValueError("Either shape and or data must not be None")
            if dtype is None:
                dtype = 'f8'
        else:
            data = np.ascontiguousarray(data)
            if dtype is None:
                dtype = data.dtype
            if shape is not None:
                if shape != data.shape:
                    raise ValueError("Shape must equal data.shape")
            else:
                shape = data.shape
        da = self._create_data_array(name, array_type, dtype, shape)
        if data is not None:
            da.write_direct(data)
        return da

    def find_sources(self, filtr=lambda _: True, limit=None):
        """
        Get all sources in this block recursively.

        This method traverses the tree of all sources in the block. The
        traversal is accomplished via breadth first and can be limited in
        depth.  On each node or source a filter is applied. If the filter
        returns true the respective source will be added to the result list.
        By default a filter is used that accepts all sources.

        :param filtr: A filter function
        :type filtr:  function
        :param limit: The maximum depth of traversal
        :type limit:  int

        :returns: A list containing the matching sources.
        :rtype: list of Source
        """
        if limit is None:
            limit = maxint
        return finders._find_sources(self, filtr, limit)

    @property
    def sources(self):
        """
        A property containing all sources of a block. Sources can be obtained
        via their index or by their id. Sources can be deleted from the list.
        Adding sources is done using the Blocks create_source method.
        This is a read only attribute.

        :type: ProxyList of Source entities.
        """
        if not hasattr(self, "_sources"):
            setattr(self, "_sources", SourceProxyList(self))
        return self._sources

    @property
    def multi_tags(self):
        """
        A property containing all multi tags of a block. MultiTag entities can
        be obtained via their index or by their id. Tags can be deleted from
        the list. Adding tags is done using the Blocks create_multi_tag method.
        This is a read only attribute.

        :type: ProxyList of MultiTag entities.
        """
        if not hasattr(self, "_multi_tags"):
            setattr(self, "_multi_tags", MultiTagProxyList(self))
        return self._multi_tags

    @property
    def tags(self):
        """
        A property containing all tags of a block. Tag entities can be obtained
        via their index or by their id. Tags can be deleted from the list.
        Adding tags is done using the Blocks create_tag method.
        This is a read only attribute.

        :type: ProxyList of Tag entities.
        """
        if not hasattr(self, "_tags"):
            setattr(self, "_tags", TagProxyList(self))
        return self._tags

    @property
    def data_arrays(self):
        """
        A property containing all data arrays of a block. DataArray entities
        can be obtained via their index or by their id. Data arrays can be
        deleted from the list. Adding a data array is done using the Blocks
        create_data_array method.
        This is a read only attribute.

        :type: ProxyList of DataArray entities.
        """
        if not hasattr(self, "_data_arrays"):
            setattr(self, "_data_arrays", DataArrayProxyList(self))
        return self._data_arrays

    @property
    def groups(self):
        """
        A property containing all groups of a block. Group entities can be
        obtained via their index or by their id. Groups can be deleted from the
        list. Adding a Group is done using the Blocks create_group method.
        This is a read only attribute.

        :type: ProxyList of Group entities.
        """
        if not hasattr(self, "_groups"):
            setattr(self, "_groups", GroupProxyList(self))
        return self._groups

    def __eq__(self, other):
        """
        Two blocks are considered equal when they have the same id.
        """
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class,
        implemented or escaped
        """
        return hash(self.id)
