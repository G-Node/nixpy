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

from nix.file import SectionProxyList

class SectionMixin(Section):

    class __metaclass__(Inject, Section.__class__):
        pass

    @property
    def sections(self):
        if not hasattr(self, "_sections"):
            setattr(self, "_sections", SectionProxyList(self))
        return self._sections

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False
