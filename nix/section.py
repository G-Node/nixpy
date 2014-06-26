# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import Section
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList

from nix.file import SectionProxyList

class PropertyProxyList(ProxyList):

    def __init__(self, obj):
        super(PropertyProxyList, self).__init__(obj, "_property_count", "_get_property_by_id",
                                                "_get_property_by_pos", "_delete_property_by_id")

class SectionMixin(Section):

    class __metaclass__(Inject, Section.__class__):
        pass

    @property
    def sections(self):
        if not hasattr(self, "_sections"):
            setattr(self, "_sections", SectionProxyList(self))
        return self._sections

    @property
    def properties(self):
        if not hasattr(self, "_properties"):
            setattr(self, "_properties", PropertyProxyList(self))
        return self._properties

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False
