# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import nixio.core

from nixio.file import FileMixin
from nixio.block import BlockMixin
from nixio.section import SectionMixin
from nixio.property import PropertyMixin
from nixio.group import GroupMixin
from nixio.data_array import (DataSetMixin, DataArrayMixin,
                              SetDimensionMixin, RangeDimensionMixin,
                              SampleDimensionMixin)
from nixio.source import SourceMixin
from nixio.tag import TagMixin
from nixio.multi_tag import MultiTagMixin
from nixio.entity_with_sources import EntityWithSourcesMixin

excludes = ("__module__", "__metaclass__", "__dict__", "__doc__")


def inject(bases, dct):
    """
    Does monkey patching to the classes in 'bases' by adding
    methods from the given dict 'dct'.
    """
    for base in bases:
        for k, v in dct.items():
            if k not in excludes:
                setattr(base, k, v)


inject((nixio.core.File,),  dict(FileMixin.__dict__))
inject((nixio.core.Section,), dict(SectionMixin.__dict__))
inject((nixio.core.Property,), dict(PropertyMixin.__dict__))
inject((nixio.core.Block,), dict(BlockMixin.__dict__))
inject((nixio.core.Group,), dict(GroupMixin.__dict__))
inject((nixio.core.DataArray,), dict(DataArrayMixin.__dict__))
inject((nixio.core.DataSet,), dict(DataSetMixin.__dict__))
inject((nixio.core.Tag,), dict(TagMixin.__dict__))
inject((nixio.core.MultiTag,), dict(MultiTagMixin.__dict__))
inject((nixio.core.Source,), dict(SourceMixin.__dict__))
inject((nixio.core.SetDimension,), dict(SetDimensionMixin.__dict__))
inject((nixio.core.RangeDimension,), dict(RangeDimensionMixin.__dict__))
inject((nixio.core.SampledDimension,), dict(SampleDimensionMixin.__dict__))
inject((nixio.core.Group,), dict(EntityWithSourcesMixin.__dict__))
inject((nixio.core.DataArray,), dict(EntityWithSourcesMixin.__dict__))
inject((nixio.core.Tag,), dict(EntityWithSourcesMixin.__dict__))
inject((nixio.core.MultiTag,), dict(EntityWithSourcesMixin.__dict__))
