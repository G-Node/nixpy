# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity_with_metadata import EntityWithMetadata
from .source import Source
from .container import LinkContainer


class EntityWithSources(EntityWithMetadata):

    def __init__(self, nixparent, h5group):
        super(EntityWithSources, self).__init__(nixparent, h5group)
        self._sources = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_):
        newentity = super(EntityWithSources, cls)._create_new(
            nixparent, h5parent, name, type_
        )
        return newentity

    @property
    def sources(self):
        """
        A property containing all Sources referenced by the group. Sources
        can be obtained by index or their id.  Sources can be removed from the
        list, but removing a referenced Source will not remove it from the
        file. New Sources can be added using the append method of the list.
        This is a read only attribute.
        """
        if self._sources is None:
            self._sources = LinkContainer("sources", self, Source,
                                          self._parent.sources)
        return self._sources
