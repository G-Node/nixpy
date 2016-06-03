# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity_with_metadata import EntityWithMetadata
from .source import Source
from .util import util


class EntityWithSources(EntityWithMetadata):

    def __init__(self, h5group):
        super(EntityWithSources, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(EntityWithSources, cls)._create_new(parent,
                                                              name, type_)
        newentity._h5group.open_group("sources")
        return newentity

    # Source
    def _get_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        return Source(sources.get_by_id(id_or_name))

    def _get_source_by_pos(self, pos):
        sources = self._h5group.open_group("sources")
        return Source(sources.get_by_pos(pos))

    def _delete_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        sources.delete(id_or_name)

    def _source_count(self):
        sources = self._h5group.open_group("sources")
        return len(sources)


util.create_link_methods(EntityWithSources, Source, "source")
EntityWithSources._remove_source_by_id = EntityWithSources._delete_source_by_id
