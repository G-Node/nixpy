# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

# NIX object classes
from .file import File
from .block import Block
from .group import Group
from .data_array import DataArray
from .tag import Tag
from .multi_tag import MultiTag
from .source import Source
from .section import Section, S
from .property import Property, OdmlType
from .feature import Feature
from .data_frame import DataFrame
from .dimensions import SampledDimension, RangeDimension, SetDimension, IndexMode
from . import validator

# enums
from .file import FileMode
from .data_array import DataSliceMode
from .datatype import DataType
from .dimension_type import DimensionType
from .link_type import LinkType
from .compression import Compression
from .tag import SliceMode

# version
from .info import VERSION

__all__ = ("File", "Block", "Group", "DataArray", "DataFrame", "Tag",
           "MultiTag", "Source", "Section", "S", "Feature", "Property",
           "OdmlType", "SampledDimension", "RangeDimension", "SetDimension",
           "FileMode", "DataSliceMode", "DataType", "DimensionType",
           "LinkType", "Compression",  "SliceMode", "IndexMode", "validator")
__author__ = ('Christian Kellner, Adrian Stoewer, Andrey Sobolev, Jan Grewe, '
              'Balint Morvai, Achilleas Koutsou')
__version__ = VERSION
