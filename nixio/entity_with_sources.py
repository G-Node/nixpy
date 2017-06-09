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
from . import util


class SourceLinkContainer(LinkContainer):

    # TODO: Sources returned from this container have an incorrect _parent
    # This is the same issue that we have with Sections. It should probably be
    # solved the same way

    def append(self, item):
        if util.is_uuid(item):
            item = self._inst_item(self._backend.get_by_id(item))

        if not hasattr(item, "id"):
            raise TypeError("NIX entity or id string required for append")

        if not self._itemstore._parent.find_sources(
                filtr=lambda x: x.id == item.id
        ):
            raise RuntimeError("This item cannot be appended here.")

        self._backend.create_link(item, item.id)


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
        can be obtained by index or their id. Sources can be removed from the
        list, but removing a referenced Source will not remove it from the
        file. New Sources can be added using the append method of the list.
        This is a read only attribute.
        """
        if self._sources is None:
            self._sources = SourceLinkContainer("sources", self, Source,
                                                self._parent.sources)
        return self._sources
