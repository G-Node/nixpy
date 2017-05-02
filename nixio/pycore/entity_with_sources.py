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

    def __init__(self, nixparent, h5group):
        super(EntityWithSources, self).__init__(nixparent, h5group)

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_):
        newentity = super(EntityWithSources, cls)._create_new(
            nixparent, h5parent, name, type_
        )
        return newentity

    # Source
    def _get_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        if util.is_uuid(id_or_name):
            id_ = id_or_name
        else:
            for grp in sources:
                if grp.get_attr("name") == id_or_name:
                    id_ = grp.get_attr("entity_id")
                    break
            else:
                raise ValueError("No Source with name {} found {}.sources"
                                 .format(id_or_name, self.name))
        return Source(self, sources.get_by_name(id_))

    def _get_source_by_pos(self, pos):
        sources = self._h5group.open_group("sources")
        return Source(self, sources.get_by_pos(pos))

    def _remove_source_by_id(self, id_):
        sources = self._h5group.open_group("sources")
        sources.delete(id_)

    def _source_count(self):
        sources = self._h5group.open_group("sources")
        return len(sources)

    def _add_source_by_id(self, id_):
        parblock = self._parent
        target = parblock._h5group.find_children(
            filtr=lambda x: x.get_attr("entity_id") == id_
        )
        cls = type(self).__name__
        if not target:
            raise RuntimeError("{}._add_source_by_id: "
                               "Source not found!".format(cls))
        if len(target) > 1:
            raise RuntimeError("{}._add_source_by_id: "
                               "Invalid data found in NIX file. "
                               "Multiple Sources found with the same ID."
                               .format(cls))
        target = Source(parblock, target[0])
        sources = self._h5group.open_group("sources")
        sources.create_link(target, target.id)

    def _has_source_by_id(self, id_or_name):
        sources = self._h5group.open_group("sources")
        sources.has_by_id(id_or_name)
