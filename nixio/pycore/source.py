# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

from .entity_with_metadata import EntityWithMetadata
from ..source import SourceMixin
from . import exceptions
from . import util


class Source(EntityWithMetadata, SourceMixin):

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
