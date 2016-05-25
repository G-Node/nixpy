# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.


class DimensionType(object):
    Sample = 1
    Range = 2
    Set = 3


class Dimension(object):

    def __init__(self):
        self.index = None
        self.dimension_type = None
        self.label = None


class SampledDimension(Dimension):

    def __init__(self):
        super(SampledDimension, self).__init__()
        self.unit = None
        self.sampling_interval = None
        self.offset = None

    def position_at(self):
        pass

    def index_of(self):
        pass


class RangeDimension(Dimension):

    def __init__(self):
        super(RangeDimension, self).__init__()
        self.unit = None
        self.ticks = None

    def index_of(self):
        pass

    def tick_at(self):
        pass


class SetDimension(Dimension):

    def __init__(self):
        super(SetDimension).__init__()
