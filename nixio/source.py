# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from sys import maxsize as maxint

from .entity_with_metadata import EntityWithMetadata
from .util.proxy_list import ProxyList
from .import exceptions
from . import util
from .util import find as finders


class SourceProxyList(ProxyList):

    def __init__(self, obj):
        super(SourceProxyList, self).__init__(obj, "_source_count",
                                              "_get_source_by_id",
                                              "_get_source_by_pos",
                                              "_delete_source_by_id")


class Source(EntityWithMetadata):

    def __init__(self, nixparent, h5group):
        super(Source, self).__init__(nixparent, h5group)
        # TODO: Validate Source container

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_):
        newentity = super(Source, cls)._create_new(nixparent, h5parent,
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
        src = Source._create_new(self, sources, name, type_)
        return src

    # Source
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

    @property
    def referring_objects(self):
        objs = []
        objs.extend(self.referring_data_arrays)
        objs.extend(self.referring_tags)
        objs.extend(self.referring_multi_tags)
        return objs

    @property
    def referring_data_arrays(self):
        return [da for da in self._parent.data_arrays if self in da.sources]

    @property
    def referring_tags(self):
        return [tg for tg in self._parent.tags if self in tg.sources]

    @property
    def referring_multi_tags(self):
        return [mt for mt in self._parent.multi_tags if self in mt.sources]

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
        A property containing all sources of a block. Sources can be obtained
        via their index or by their id. Sources can be deleted from the list.
        Adding sources is done using the Blocks create_source method.
        This is a read only attribute.

        :type: ProxyList of Source entities.
        """
        if not hasattr(self, "_sources"):
            setattr(self, "_sources", SourceProxyList(self))
        return self._sources

    def __eq__(self, other):
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
