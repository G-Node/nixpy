# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

from .entity_with_metadata import EntityWithMetadata
from ..entity_with_sources import EntityWithSourcesMixin
from .source import Source

from . import util


class EntityWithSources(EntityWithMetadata, EntityWithSourcesMixin):

    def __init__(self, h5group):
        super(EntityWithSources, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(EntityWithSources, cls)._create_new(parent,
                                                              name, type_)
        return newentity

    # Source
    def _get_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        if not util.is_uuid(id_or_name):
            parblock = self._h5group.root
            id_or_name = parblock.sources[id_or_name].id
        return Source(sources.get_by_name(id_or_name))

    def _get_source_by_pos(self, pos):
        sources = self._h5group.open_group("sources")
        return Source(sources.get_by_pos(pos))

    def _remove_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        sources.delete(id_or_name)

    def _source_count(self):
        sources = self._h5group.open_group("sources")
        return len(sources)

    def _add_source_by_id(self, id_or_name):
        parblock = self._h5group.root
        if id_or_name not in parblock.sources:
            cls = type(self).__name__
            raise RuntimeError("{}._add_source_by_id: "
                               "Source not found in Block!".format(cls))
        target = parblock.sources[id_or_name]
        sources = self._h5group.open_group("sources")
        sources.create_link(target, target.id)

    def _has_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        sources.has_by_id(id_or_name)

