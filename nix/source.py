# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import Source
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList

from nix.block import SourceProxyList

class SourceMixin(Source):

    class __metaclass__(Inject):
        pass

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
