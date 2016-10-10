# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

from nixio.pycore.file import File, FileMode
from nixio.value import Value, DataType
from nixio.dimension_type import DimensionType
from nixio.link_type import LinkType

from nixio.section import S

try:
    import nixio.util.inject
except ImportError:
    pass

import sys
import os

__all__ = ("File", "FileMode", "DataType", "Value", "LinkType", "DimensionType")

__author__ = ('Christian Kellner, Adrian Stoewer, Andrey Sobolev, Jan Grewe,'
              ' Balint Morvai')

_nixio_bin = os.path.join(sys.prefix, 'share', 'nixio', 'bin')
if os.path.isdir(_nixio_bin):
    os.environ["PATH"] += os.pathsep + _nixio_bin
