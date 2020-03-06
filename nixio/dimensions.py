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
from .data_frame import DataFrame
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
        }[DimensionType(item.get_attr("dimension_type"))]
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
        return DimensionType(self._h5group.get_attr("dimension_type"))

    @dimension_type.setter
    def _dimension_type(self, dimtype):
        dimtype = DimensionType(dimtype)
        if dimtype not in DimensionType:
            raise TypeError("Invalid dimension type.")
        self._h5group.set_attr("dimension_type", dimtype.value)

    @property
    def index(self):
        return self.dim_index

    def __str__(self):
        return "{}: {{index = {}}}".format(
            type(self).__name__, self.index
        )

    def __repr__(self):
        return self.__str__()


class SampledDimension(Dimension):

    def __init__(self, h5group, index):
        super(SampledDimension, self).__init__(h5group, index)

    @classmethod
    def _create_new(cls, parent, index, sample):
        newdim = super(SampledDimension, cls)._create_new(parent, index)
        newdim._dimension_type = DimensionType.Sample
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
        offset = self.offset if self.offset else 0.0
        sample = self.sampling_interval
        start_val = start * sample + offset
        end_val = (start + count) * sample + offset
        return tuple(np.arange(start_val, end_val, sample))

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
        newdim._dimension_type = DimensionType.Range
        newdim._h5group.write_data("ticks", ticks, dtype=DataType.Double)
        return newdim

    @classmethod
    def _create_new_alias(cls, parent, index, da):
        newdim = super(RangeDimension, cls)._create_new(parent, index)
        newdim._dimension_type = DimensionType.Range
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
        self._h5group.write_data("ticks", ticks)

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
        pidxs = np.flatnonzero((ticks - position) <= 0)
        return int(pidxs[-1])

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
        newdim._dimension_type = DimensionType.Set
        return newdim

    @property
    def labels(self):
        labels = tuple(self._h5group.get_data("labels"))
        if len(labels) and isinstance(labels[0], bytes):
            labels = tuple(l.decode() for l in labels)
        return labels

    @labels.setter
    def labels(self, labels):
        dt = util.vlen_str_dtype
        self._h5group.write_data("labels", labels, dtype=dt)


class DataFrameDimension(Dimension):

    def __init__(self, h5group, index):
        super(DataFrameDimension, self).__init__(h5group, index)

    @classmethod
    def _create_new(cls, parent, index, data_frame, column):
        """
        Create a new Dimension that points to a DataFrame
        :param parent: DataArray the dimension will be attached to
        :param data_frame: the referenced DataFrame for this Dimension
        :param column: the index of a column in the DataFrame that the Dimension will reference (optional)
        :return: The new DataFrameDimension
        """
        newdim = super(DataFrameDimension, cls)._create_new(parent, index)
        newdim.data_frame = data_frame
        newdim.column = column
        newdim._dimension_type = DimensionType.DataFrame
        return newdim

    def unit(self, index=None):
        if index is None:
            if self.column is None:
                raise ValueError("No default column index is set for this Dimension. Please supply one")
            else:
                idx = self.column
        else:
            idx = index
        unit = self.data_frame.units[idx]
        return unit

    def ticks(self, index=None):
        if index is None:
            if self.column is None:
                raise ValueError("No default column index is set for this Dimension. Please supply one")
            else:
                idx = self.column
        else:
            idx = index
        df = self.data_frame
        ticks = df[df.column_names[idx]]
        return ticks

    def label(self, index=None):
        if index is None:
            if self.column is None:
                label = self.data_frame.name
            else:
                label = self.data_frame.column_names[self.column]
        else:
            label = self.data_frame.column_names[index]
        return label

    @property
    def data_frame(self):
        dfname = self._h5group.get_by_pos(0).name
        grp = self._h5group.open_group(dfname)
        df = DataFrame(grp.h5root.group["data_frames"], grp)
        return df

    @data_frame.setter
    def data_frame(self, df):
        self._h5group.create_link(df, df.id)

    @property
    def column(self):
        colidx = self._h5group.get_attr("column")
        return colidx

    @column.setter
    def column(self, col):
        self._h5group.set_attr("column", col)
