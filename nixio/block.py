# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

try:
    from sys import maxint
except ImportError:
    from sys import maxsize as maxint
import numpy as np

from .util import find as finders
from .compression import Compression

from .entity import Entity
from .exceptions import exceptions
from .group import Group
from .data_array import DataArray
from .multi_tag import MultiTag
from .tag import Tag
from .source import Source
from . import util
from .container import Container, SourceContainer
from .section import Section


class Block(Entity):

    def __init__(self, nixparent, h5group, compression=Compression.Auto):
        super(Block, self).__init__(nixparent, h5group)
        self._groups = None
        self._data_arrays = None
        self._tags = None
        self._multi_tags = None
        self._sources = None
        self._compr = compression

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, compression):
        newentity = super(Block, cls)._create_new(nixparent, h5parent,
                                                  name, type_)
        newentity._compr = compression
        return newentity

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

    def create_data_array(self, name, array_type, dtype=None, shape=None,
                          data=None, compression=Compression.Auto):
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
        :param compression: En-/disable dataset compression.
        :type compression: :class:`~nixio.Compression`

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
        util.check_entity_name_and_type(name, array_type)
        data_arrays = self._h5group.open_group("data_arrays")
        if name in data_arrays:
            raise exceptions.DuplicateName("create_data_array")
        if compression == Compression.Auto:
            compression = self._compr
        da = DataArray._create_new(self, data_arrays, name, array_type,
                                   dtype, shape, compression)
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
        """
        if self._sources is None:
            self._sources = SourceContainer("sources", self, Source)
        return self._sources

    @property
    def multi_tags(self):
        """
        A property containing all multi tags of a block. MultiTag entities can
        be obtained via their index or by their id. Tags can be deleted from
        the list. Adding tags is done using the Blocks create_multi_tag method.
        This is a read only attribute.
        """
        if self._multi_tags is None:
            self._multi_tags = Container("multi_tags", self, MultiTag)
        return self._multi_tags

    @property
    def tags(self):
        """
        A property containing all tags of a block. Tag entities can be obtained
        via their index or by their id. Tags can be deleted from the list.
        Adding tags is done using the Blocks create_tag method.
        This is a read only attribute.
        """
        if self._tags is None:
            self._tags = Container("tags", self, Tag)
        return self._tags

    @property
    def data_arrays(self):
        """
        A property containing all data arrays of a block. DataArray entities
        can be obtained via their index or by their id. Data arrays can be
        deleted from the list. Adding a data array is done using the Blocks
        create_data_array method.
        This is a read only attribute.
        """
        if self._data_arrays is None:
            self._data_arrays = Container("data_arrays", self, DataArray)
        return self._data_arrays

    @property
    def groups(self):
        """
        A property containing all groups of a block. Group entities can be
        obtained via their index or by their id. Groups can be deleted from the
        list. Adding a Group is done using the Blocks create_group method.
        This is a read only attribute.
        """
        if self._groups is None:
            self._groups = Container("groups", self, Group)
        return self._groups

    def __eq__(self, other):
        """
        Two Blocks are considered equal when they have the same id.
        """
        if hasattr(other, "id"):
            return self.id == other.id
        return False

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class,
        implemented or escaped
        """
        return hash(self.id)

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
