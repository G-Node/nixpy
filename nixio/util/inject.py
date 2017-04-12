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
