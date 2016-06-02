# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity_with_metadata import EntityWithMetadata
from ..source import SourceMixin
from . import util
from . import exceptions


class Source(EntityWithMetadata, SourceMixin):

    def __init__(self, h5obj):
        super(Source, self).__init__(h5obj)
        # TODO: Validate Source container

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Source, cls)._create_new(parent, name, type_)
        newentity._h5obj.create_group("sources")
        return newentity

    # Source
    def create_source(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        sources = self._h5obj["sources"]
        if name in sources:
            raise exceptions.DuplicateName("create_source")
        src = Source._create_new(sources, name, type_)
        return src

    # Source
    def _get_source_by_id(self, id_or_name):
        return Source(util.id_or_name_getter(self._h5obj["sources"], id_or_name))

    def _get_source_by_pos(self, pos):
        return Source(util.pos_getter(self._h5obj["sources"], pos))

    def _delete_source_by_id(self, id_or_name):
        util.deleter(self._h5obj["sources"], id_or_name)

    def _source_count(self):
        return len(self._h5obj["sources"])
