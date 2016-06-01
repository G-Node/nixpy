# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import NamedEntity
from .section import Section


class EntityWithMetadata(NamedEntity):

    def __init__(self, h5obj):
        super(EntityWithMetadata, self).__init__(h5obj)
        # TODO: Additional validation for metadata

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(EntityWithMetadata, cls)._create_new(parent,
                                                               name, type_)
        return newentity

    @property
    def metadata(self):
        return Section(self._h5obj["metadata"])
