# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from numbers import Number

import numpy as np

from .datatype import DataType
from .dimension_type import DimensionType
from . import util
from .container import Container


class DimensionContainer(Container):
    """
    DimensionContainer extends Container to support returning different types
    of Dimension classes on return.
    """

    def _inst_item(self, item):
        cls = {
            DimensionType.Range: RangeDimension,
            DimensionType.Sample: SampledDimension,
            DimensionType.Set: SetDimension,
        }[item.get_attr("dimension_type")]
        idx = item.name
        return cls(item, idx)


class Dimension(object):

    def __init__(self, h5group, index):
        self._h5group = h5group
        self.dim_index = int(index)

    @classmethod
    def _create_new(cls, parent, index):
        h5group = parent.open_group(str(index))
        newdim = cls(h5group, index)
        return newdim

    @property
    def dimension_type(self):
        return self._h5group.get_attr("dimension_type")

    @dimension_type.setter
    def dimension_type(self, dimtype):
        if dimtype not in (DimensionType.Sample, DimensionType.Range,
                           DimensionType.Set):
            raise ValueError("Invalid dimension type.")
        self._h5group.set_attr("dimension_type", dimtype)

    @property
    def index(self):
        return self.dim_index


class SampledDimension(Dimension):

    def __init__(self, h5group, index):
        super(SampledDimension, self).__init__(h5group, index)

    @classmethod
    def _create_new(cls, parent, index, sample):
        newdim = super(SampledDimension, cls)._create_new(parent, index)
        newdim.dimension_type = DimensionType.Sample
        newdim.sampling_interval = sample
        return newdim

    def position_at(self, index):
        """
        Returns the position corresponding to a given index.

        :param index: A positive integer.

        :returns: The position matching to the index.
        :rtype: float
        """
        offset = self.offset if self.offset else 0
        sample = self.sampling_interval
        return index * sample + offset

    def index_of(self, position):
        """
        Returns the index of a certain position in the dimension.

        :param position: The position.

        :returns: The nearest index.
        :rtype: int
        """
        offset = self.offset if self.offset else 0
        sample = self.sampling_interval
        index = np.round((position - offset) / sample)
        if index < 0:
            raise IndexError("Position is out of bounds of this dimension!")
        return int(index)

    def axis(self, count, start=0):
        """
        Get an axis as defined by this sampled dimension.

        :param count: A positive integer specifying the length of the axis
        (no of samples).
        :param start: positive integer, indicates the starting sample.

        :returns: The created axis
        :rtype: list
        """
        offset = self.offset if self.offset else 0
        sample = self.sampling_interval
        end = (count + start) * sample + offset
        return tuple(np.arange(offset, end, sample))

    @property
    def label(self):
        return self._h5group.get_attr("label")

    @label.setter
    def label(self, l):
        util.check_attr_type(l, str)
        self._h5group.set_attr("label", l)

    @property
    def sampling_interval(self):
        return self._h5group.get_attr("sampling_interval")

    @sampling_interval.setter
    def sampling_interval(self, interval):
        util.check_attr_type(interval, Number)
        self._h5group.set_attr("sampling_interval", interval)

    @property
    def unit(self):
        return self._h5group.get_attr("unit")

    @unit.setter
    def unit(self, u):
        util.check_attr_type(u, str)
        self._h5group.set_attr("unit", u)

    @property
    def offset(self):
        return self._h5group.get_attr("offset")

    @offset.setter
    def offset(self, o):
        util.check_attr_type(o, Number)
        self._h5group.set_attr("offset", o)


class RangeDimension(Dimension):

    def __init__(self, h5group, index):
        super(RangeDimension, self).__init__(h5group, index)

    @classmethod
    def _create_new(cls, parent, index, ticks):
        newdim = super(RangeDimension, cls)._create_new(parent, index)
        newdim.dimension_type = DimensionType.Range
        ticksds = newdim._h5group.create_dataset("ticks",
                                                 shape=np.shape(ticks),
                                                 dtype=DataType.Double)
        ticksds.write_data(ticks)
        return newdim

    @classmethod
    def _create_new_alias(cls, parent, index, da):
        newdim = super(RangeDimension, cls)._create_new(parent, index)
        newdim.dimension_type = DimensionType.Range
        newdim._h5group.create_link(da, da.id)
        return newdim

    @property
    def is_alias(self):
        """
        Return True if this dimension is an Alias Range dimension.
        Read-only property.
        """
        if self._h5group.has_data("ticks"):
            return False
        return True

    @property
    def ticks(self):
        g = self._redirgrp
        if g.has_data("ticks"):
            ticks = g.get_data("ticks")
        elif g.has_data("data"):
            ticks = g.get_data("data")
        else:
            raise AttributeError("Attribute 'ticks' is not set.")
        return tuple(ticks)

    @ticks.setter
    def ticks(self, ticks):
        if np.any(np.diff(ticks) < 0):
            raise ValueError("Ticks are not given in an ascending order.")
        ticksds = self._h5group.get_dataset("ticks")
        ticksds.write_data(ticks)

    @property
    def _redirgrp(self):
        """
        If the dimension is an Alias Range dimension, this property returns
        the H5Group of the linked DataArray. Otherwise, it returns the H5Group
        representing the dimension.
        """
        if self.is_alias:
            gname = self._h5group.get_by_pos(0).name
            return self._h5group.open_group(gname)
        return self._h5group

    @property
    def label(self):
        return self._redirgrp.get_attr("label")

    @label.setter
    def label(self, l):
        util.check_attr_type(l, str)
        self._redirgrp.set_attr("label", l)

    @property
    def unit(self):
        return self._redirgrp.get_attr("unit")

    @unit.setter
    def unit(self, u):
        util.check_attr_type(u, str)
        self._redirgrp.set_attr("unit", u)

    def index_of(self, position):
        """
        Returns the index of a certain position in the dimension.

        :param position: The position.

        :returns: The nearest index.
        :rtype: int
        """
        ticks = self.ticks
        if position < ticks[0]:
            return 0
        elif position > ticks[-1]:
            return len(ticks) - 1

        ticks = np.array(ticks)
        pidxs = np.flatnonzero((ticks - position) >= 0)
        return int(pidxs[0])

    def tick_at(self, index):
        """
        Returns the tick at the given index. Will throw an Exception if the
        index is out of bounds.

        :param index: The index.

        :returns: The corresponding position.
        :rtype: double
        """
        ticks = list(self.ticks)
        return ticks[index]

    def axis(self, count, start=0):
        """
        Get an axis as defined by this range dimension.

        :param count: A positive integer specifying the length of the axis
        (no of points).
        :param start: positive integer, indicates the starting tick.

        :returns: The created axis
        :rtype: list
        """
        ticks = self.ticks
        end = start + count
        if end > len(ticks):
            raise IndexError("RangeDimension.axis: Count is invalid, "
                             "reaches beyond the ticks stored in this "
                             "dimension.")
        return ticks[start:end]


class SetDimension(Dimension):

    def __init__(self, h5group, index):
        super(SetDimension, self).__init__(h5group, index)

    @classmethod
    def _create_new(cls, parent, index):
        newdim = super(SetDimension, cls)._create_new(parent, index)
        newdim.dimension_type = DimensionType.Set
        return newdim

    @property
    def labels(self):
        labels = tuple(self._h5group.get_data("labels"))
        if len(labels) and isinstance(labels[0], bytes):
            labels = tuple(l.decode() for l in labels)
        return labels

    @labels.setter
    def labels(self, labels):
        lshape = np.shape(labels)
        dt = util.vlen_str_dtype
        labelsds = self._h5group.create_dataset("labels", shape=lshape,
                                                dtype=dt)
        labelsds.write_data(labels)
