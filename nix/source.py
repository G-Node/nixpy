# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function, unicode_literals)

import sys

import nix.util.find as finders
from nix.core import Source
from nix.util.inject import inject
from nix.util.proxy_list import ProxyList

from nix.block import SourceProxyList

try:
    from sys import maxint
except:
    from sys import maxsize as maxint


class SourceMixin(Source):

    def find_sources(self, filtr=lambda _ : True, limit=maxint):
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

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class, implemented or escaped
        """
        return hash(self.id)


inject((Source,), dict(SourceMixin.__dict__))
