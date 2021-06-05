# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from sys import maxsize as maxint

from .import exceptions
from .entity import Entity
from .container import SourceContainer
from . import util
from .util import find as finders
from .section import Section


class Source(Entity):

    def __init__(self, nixfile, nixparent, h5group):
        super(Source, self).__init__(nixfile, nixparent, h5group)
        self._sources = None
        self._parent_block = None

    @classmethod
    def create_new(cls, nixfile, nixparent, h5parent, name, type_):
        newentity = super(Source, cls).create_new(nixfile, nixparent, h5parent,
                                                  name, type_)
        return newentity

    # Source
    def create_source(self, name, type_):
        """
        Create a new source as a child of the current Source.

        :param name: The name of the source to create.
        :type name: str
        :param type_: The type of the source.
        :type type_: str

        :returns: The newly created source.
        :rtype: Source
        """
        util.check_entity_name_and_type(name, type_)
        sources = self._h5group.open_group("sources", True)
        if name in sources:
            raise exceptions.DuplicateName("create_source")
        src = Source.create_new(self.file, self, sources, name, type_)
        return src

    @property
    def parent_block(self):
        """
        Returns the block this source is contained in.

        :returns: the Block containing this source
        :rtype: Block
        """
        if self._parent_block is not None:
            return self._parent_block
        maybe_block = self._parent
        if not hasattr(maybe_block, "data_arrays"):
            maybe_block = maybe_block.parent_block
        self._parent_block = maybe_block
        return self._parent_block

    def _find_parent_recursive(self, child_id, check_id=True):
        """
        Find the parent source of this source. Search is based on the ID of of a child source. Searching by name might be ambiguous.
        By default it will raise an ValueError if the child_id does not look like an UUID.

        :param child_id: The ID of the child whose parent is searched.
        :type child_id: str
        :param check_id: Controls whether or not to check if the child_is looks like an UUID. Defaults to True.
        :type check_id: bool

        :returns: the parent source, if any, otherwise None.
        :rtype: Source
        """
        if check_id and not util.is_uuid(child_id):
            raise ValueError("Error calling find_parent_source: argument child_id (%s) does not look like an UUID " % child_id)
        if child_id in self.sources:
            return self
        else:
            for s in self.sources:
                src = s._find_parent_recursive(child_id, False)
                if src is not None:
                    return src
        return None

    @property
    def parent_source(self):
        """
        Get the parent source of this source. If this source is at the root, None will be returned

        :returns: the parent source
        :rtype: Source or None
        """
        # for now we need to do a search
        block = self.parent_block
        if self in block.sources:
            return None
        for s in block.sources:
            p = s._find_parent_recursive(self.id, False)
            if p is not None:
                return p
        return None

    @property
    def referring_objects(self):
        """
        Returns the list of entities that link to this source.

        :returns: all objects referring to this source.
        :rtype: list
        """
        objs = []
        objs.extend(self.referring_data_arrays)
        objs.extend(self.referring_tags)
        objs.extend(self.referring_multi_tags)
        return objs

    @property
    def referring_data_arrays(self):
        """
        Returns all DataArray entities linking to this source.

        :returns: all DataArrays referring to this source.
        :rtype: list
        """
        block = self.parent_block
        return [da for da in block.data_arrays if self in da.sources]

    @property
    def referring_tags(self):
        """
        Returns all Tag entities linking to this source.

        :returns: all Tags referring to this source.
        :rtype: list
        """
        block = self.parent_block
        return [tg for tg in block.tags if self in tg.sources]

    @property
    def referring_multi_tags(self):
        """
        Returns all MultiTag entities linking to this source.

        :returns: all MultiTags referring to this source.
        :rtype: list
        """
        block = self.parent_block
        return [mt for mt in block.multi_tags if self in mt.sources]

    def find_sources(self, filtr=lambda _: True, limit=None):
        """
        Get all child sources of this source recursively.

        This method traverses the tree of all sources. The traversal
        is accomplished via breadth first and can be limited in depth. On each
        node or source a filter is applied. If the filter returns true the
        respective source will be added to the result list.
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
        A property containing child sources of a Source. Sources can be
        obtained via their name, index, id. Sources can be deleted from the
        list. Adding sources is done using the Blocks create_source method.
        This is a read only attribute.
        """
        if self._sources is None:
            self._sources = SourceContainer("sources", self.file, self, Source)
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
            return Section(self.file, None, self._h5group.open_group("metadata"))
        else:
            return None

    @metadata.setter
    def metadata(self, sect):
        """
        Setter for the metadata section that contains meta information about this Source.

        :param sect: The metadata section.
        :type sect: Section

        :raises: TypeError if sect is not of type Section
        """
        if not isinstance(sect, Section):
            raise TypeError("{} is not of type Section".format(sect))
        self._h5group.create_link(sect, "metadata")

    @metadata.deleter
    def metadata(self):
        if "metadata" in self._h5group:
            self._h5group.delete("metadata")
