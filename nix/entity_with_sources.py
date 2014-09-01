# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import DataArray, MultiTag, Tag
from nix.util.inject import Inject
from nix.util.proxy_list import RefProxyList

class RefSourceProxyList(RefProxyList):

    def __init__(self, obj):
        super(RefSourceProxyList, self).__init__(obj, "_source_count", "_get_source_by_id",
                    "_get_source_by_pos", "_remove_source_by_id", "_add_source_by_id")

_sources_doc = """
Getter for sources.
"""

def _get_sources(self):
    if not hasattr(self, "_sources"):
        setattr(self, "_sources", RefSourceProxyList(self))
    return self._sources

class DataArrySourcesMixin(DataArray):

    class __metaclass__(Inject, DataArray.__class__):
        pass

    sources = property(_get_sources, None, None, _sources_doc)


class MultiTagSourcesMixin(MultiTag):

    class __metaclass__(Inject, MultiTag.__class__):
        pass

    sources = property(_get_sources, None, None, _sources_doc)

class TagSourcesMixin(Tag):

    class __metaclass__(Inject, Tag.__class__):
        pass

    sources = property(_get_sources, None, None, _sources_doc)
