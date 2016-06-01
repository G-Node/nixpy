# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity_with_metadata import EntityWithMetadata
from . import util
from . import exceptions


class Source(EntityWithMetadata):

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

util.create_container_methods(Source, Source, "source")
