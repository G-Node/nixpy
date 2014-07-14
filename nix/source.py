# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

import sys

import nix.util.find as finders
from nix.core import Source
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList

from nix.block import SourceProxyList

class SourceMixin(Source):

    class __metaclass__(Inject, Source.__class__):
        pass

    def find_sources(self, filtr=lambda _ : True, limit=sys.maxint):
        """
        Get all child sources of this source recursively.

        This method traverses the tree of all sources. The traversal
        is accomplished via breadth first and can be limited in depth. On each node or
        source a filter is applied. If the filter returns true the respective source
        will be added to the result list.
        By default a filter is used that accepts all sources.

        :param filtr: A filter function
        :type filtr:  function
        :param limit: The maximum depth of traversal
        :type limit:  int

        :returns: A list containing the matching sources.
        :rtype: list of Source
        """
        return finders._find_sources(self, filtr, limit)

    @property
    def sources(self):
        if not hasattr(self, "_sources"):
            setattr(self, "_sources", SourceProxyList(self))
        return self._sources

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False
