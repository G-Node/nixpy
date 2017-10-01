# Copyright (c) 2017, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from .source import Source
from .container import LinkContainer
from . import util


class SourceLinkContainer(LinkContainer):

    # TODO: Sources returned from this container have an incorrect _parent
    # This is the same issue that we have with Sections. It should probably be
    # solved the same way

    # NOTE: Source requires a different link container since a valid Source
    # may exist anywhere beneath the root Block's child sources. The check for
    # the Source's validity needs to be done with the find_sources() function
    # down the entire tree, as opposed to the default LinkContainer.append()
    # function which needs to only check the root Block's container.

    def __init__(self, parent):
        """
        LinkContainer for Sources.
        """
        super(SourceLinkContainer, self).__init__("sources", parent, Source,
                                                  parent._parent.sources)

    def append(self, item):
        if util.is_uuid(item):
            item = self._inst_item(self._backend.get_by_id(item))

        if not hasattr(item, "id"):
            raise TypeError("NIX entity or id string required for append")

        if not self._itemstore._parent.find_sources(filtr=lambda x:
                                                    x.id == item.id):
            raise RuntimeError("This item cannot be appended here.")

        self._backend.create_link(item, item.id)
