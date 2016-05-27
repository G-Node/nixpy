# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function, unicode_literals)

try:
    from nixio.core import DataArray as CDataArray
    from nixio.core import MultiTag as CMultiTag
    from nixio.core import Tag as CTag
except ImportError:
    CDataArray = None
    CMultiTag = None
    CTag = None

from nixio.pycore import DataArray, MultiTag, Tag

from nixio.util.inject import inject
from nixio.util.proxy_list import RefProxyList


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


class DataArraySourcesMixin(object):

    sources = property(_get_sources, None, None, _sources_doc)


class MultiTagSourcesMixin(object):

    sources = property(_get_sources, None, None, _sources_doc)


class TagSourcesMixin(object):

    sources = property(_get_sources, None, None, _sources_doc)


inject((DataArray, CDataArray), dict(DataArraySourcesMixin.__dict__))
inject((MultiTag, CMultiTag), dict(MultiTagSourcesMixin.__dict__))
inject((Tag, CTag), dict(TagSourcesMixin.__dict__))
