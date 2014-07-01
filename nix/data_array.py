# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import DataArray
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList


class DataArrayMixin(DataArray):

    class __metaclass__(Inject, DataArray.__class__):
        pass

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False
