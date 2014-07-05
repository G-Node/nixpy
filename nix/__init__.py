# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from nix.core import File, FileMode, Block, DataType, Section, Property, Value, \
    Source, DataArray, RangeDimension, SetDimension, SampledDimension, \
    DimensionType, Feature, LinkType, SimpleTag

from nix.block import BlockMixin
from nix.file import FileMixin
from nix.section import SectionMixin
from nix.property import PropertyMixin, ValueMixin
from nix.source import SourceMixin
from nix.data_array import DataArrayMixin
from nix.entity_with_sources import DataArrySourcesMixin, DataTagSourcesMixin, SimpleTagSourcesMixin
from nix.simple_tag import SimpleTagMixin

__all__ = ("File", "FileMode", "Block", "DataType", "Section", "Property",
           "Value", "Source", "DataArray", "RangeDimension", "SetDimension",
           "SampledDimension", "DimensionType", "Feature", "LinkType",
           "SimpleTag")

__author__ = "Christian Kellner"
