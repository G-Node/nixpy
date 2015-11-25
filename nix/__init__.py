# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

from nix.core import File, FileMode, Block, DataType, Section, Property, Value, \
    Source, DataArray, RangeDimension, SetDimension, SampledDimension, \
    DimensionType, Feature, LinkType, Tag, MultiTag, Group

from nix.block import BlockMixin
from nix.file import FileMixin
from nix.section import SectionMixin
from nix.property import PropertyMixin, ValueMixin
from nix.source import SourceMixin
from nix.data_array import DataSetMixin
from nix.data_array import DataArrayMixin
from nix.tag import TagMixin
from nix.multi_tag import MultiTagMixin
from nix.group import GroupMixin
from nix.entity_with_sources import DataArraySourcesMixin, MultiTagSourcesMixin, \
    TagSourcesMixin

from nix.section import S

__all__ = ("File", "FileMode", "Block", "DataType", "Section", "Property",
           "Value", "Source", "DataArray", "RangeDimension", "SetDimension",
           "SampledDimension", "DimensionType", "Feature", "LinkType",
           "Tag", "MultiTag", "Group")

del BlockMixin, FileMixin, SectionMixin, PropertyMixin, ValueMixin, SourceMixin, DataArrayMixin, TagMixin
del MultiTagMixin, DataArraySourcesMixin, MultiTagSourcesMixin, TagSourcesMixin, GroupMixin

__author__ = 'Christian Kellner, Adrian Stoewer, Andrey Sobolev, Jan Grewe, Balint Morvai'
