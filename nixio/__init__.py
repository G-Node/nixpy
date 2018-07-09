# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from .file import File, FileMode
from .value import Value, DataType
from .dimension_type import DimensionType
from .link_type import LinkType
from .compression import Compression
from .pycore.data_array import DataSliceMode

from .pycore.section import S

from .info import VERSION as __version__

__all__ = ("File", "FileMode", "DataType", "Value",
           "LinkType", "DimensionType")
__author__ = ('Christian Kellner, Adrian Stoewer, Andrey Sobolev, Jan Grewe, '
              'Balint Morvai, Achilleas Koutsou')
