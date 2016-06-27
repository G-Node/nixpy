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

    def __init__(self, h5group):
        super(EntityWithMetadata, self).__init__(h5group)
        # TODO: Additional validation for metadata

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(EntityWithMetadata, cls)._create_new(parent,
                                                               name, type_)
        return newentity

    @property
    def metadata(self):
        if "metadata" in self._h5group:
            return Section(self._h5group.open_group("metadata"))
        else:
            return None

    @metadata.setter
    def metadata(self, sect):
        if not isinstance(sect, Section):
            raise TypeError("Error setting metadata to {}. Not a Section."
                            .format(sect))
        self._h5group.create_link(sect, "metadata")

