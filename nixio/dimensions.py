# -*- coding: utf-8 -*-

# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from numbers import Number
try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence

import numpy as np

from .datatype import DataType
from .dimension_type import DimensionType
from .data_frame import DataFrame
from . import util
from .container import Container
from .exceptions import IncompatibleDimensions, OutOfBounds


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
            DimensionType.DataFrame: DataFrameDimension,
        }[DimensionType(item.get_attr("dimension_type"))]
        idx = item.name
        return cls(self._parent, idx)


class DimensionLink(object):
    """
    Links a Dimension to a data object (DataArray or DataFrame).

    A single vector of values from the underlying data object must be
    specified to serve as the ticks or labels for the associated Dimension.

    - A single vector of a DataArray.
    - A single column of a DataFrame.
    """

    def __init__(self, nixfile, nixparent, h5group):
        util.check_entity_id(h5group.get_attr("entity_id"))
        self._h5group = h5group
        self._parent = nixparent
        self._file = nixfile

    @classmethod
    def create_new(cls, nixfile, nixparent, h5parent, dataobj, dotype, index):
        id_ = util.create_id()
        h5group = h5parent.open_group("link", True)
        h5group.set_attr("entity_id", id_)
        newdimlink = cls(nixfile, nixparent, h5group)
        newdimlink._h5group.set_attr("data_object_type", dotype)
        newdimlink._h5group.create_link(dataobj, dataobj.id)
        newdimlink.index = index
        now = util.time_to_str(util.now_int())
        newdimlink._h5group.set_attr("created_at", now)
        newdimlink._h5group.set_attr("updated_at", now)
        return newdimlink

    @property
    def id(self):
        self._h5group.get_attr("entity_id")

    @property
    def file(self):
        return self._file

    @property
    def linked_data(self):
        grp = self._h5group.get_by_pos(0)
        return grp.get_data("data")

    @property
    def index(self):
        if self._data_object_type == "DataArray":
            return tuple(self._h5group.get_attr("index"))
        if self._data_object_type == "DataFrame":
            return self._h5group.get_attr("index")
        raise RuntimeError("Invalid DataObjectType attribute found in "
                           "DimensionLink")

    @index.setter
    def index(self, index):
        if self._data_object_type == "DataArray":
            util.check_attr_type(index, Sequence)
            if index.count(-1) != 1:
                raise ValueError("Index for DimensionLink with DataArray must "
                                 "have exactly one value equal to -1. "
                                 "See class docstring for more information.")
            self._h5group.set_attr("index", list(index))
        elif self._data_object_type == "DataFrame":
            util.check_attr_type(index, int)
            self._h5group.set_attr("index", index)
        else:
            raise RuntimeError("Invalid DataObjectType attribute found in "
                               "DimensionLink")

    @property
    def _data_object_type(self):
        return self._h5group.get_attr("data_object_type")


class Dimension(object):

    def __init__(self, nixfile, data_array, index):
        dimgroup = data_array._h5group.open_group("dimensions")
        h5group = dimgroup.open_group(str(index))
        self._h5group = h5group
        self.dim_index = int(index)
        self._parent = data_array
        self._file = nixfile

    @property
    def dimension_type(self):
        return DimensionType(self._h5group.get_attr("dimension_type"))

    def _set_dimension_type(self, dimtype):
        dimtype = DimensionType(dimtype)
        if dimtype not in DimensionType:
            raise TypeError("Invalid dimension type.")
        self._h5group.set_attr("dimension_type", dimtype.value)

    @property
    def index(self):
        return self.dim_index

    def link_data_array(self, data_array, index):
        if len(data_array.data_extent) != len(index):
            raise IncompatibleDimensions(
                "Length of linked DataArray indices ({}) does not match"
                "number of DataArray dimensions ({})".format(
                    len(data_array.data_extent), len(index)
                ),
                "Dimension.link_data_array"
            )

        if index.count(-1) != 1:
            # TODO: Add link to relevant docs
            raise ValueError(
                "Invalid linked DataArray index: "
                "One of the values must be -1, indicating the relevant vector."
            )

        DimensionLink.create_new(self._file, self, self._h5group,
                                 data_array, "DataArray", index)

    def link_data_frame(self, data_frame, index):
        if index >= len(data_frame.columns):
            raise OutOfBounds("DataFrame index is out of bounds", index)
        DimensionLink.create_new(self._file, self, self._h5group,
                                 data_frame, "DataFrame", index)

    def __str__(self):
        return "{}: {{index = {}}}".format(
            type(self).__name__, self.index
        )

    def __repr__(self):
        return self.__str__()


class SampledDimension(Dimension):

    def __init__(self, data_array, index):
        nixfile = data_array.file
        super(SampledDimension, self).__init__(nixfile, data_array, index)

    @classmethod
    def create_new(cls, data_array, index, sample):
        newdim = cls(data_array, index)
        newdim._set_dimension_type(DimensionType.Sample)
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
    def label(self, label):
        util.check_attr_type(label, str)
        self._h5group.set_attr("label", label)

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

    def __init__(self, data_array, index):
        nixfile = data_array.file
        super(RangeDimension, self).__init__(nixfile, data_array, index)

    @classmethod
    def create_new(cls, data_array, index, ticks):
        newdim = cls(data_array, index)
        newdim._set_dimension_type(DimensionType.Range)
        newdim._h5group.write_data("ticks", ticks, dtype=DataType.Double)
        return newdim

    @classmethod
    def create_new_alias(cls, data_array, index):
        newdim = cls(data_array, index)
        newdim._set_dimension_type(DimensionType.Range)
        newdim._h5group.create_link(data_array, data_array.id)
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
    def label(self, label):
        util.check_attr_type(label, str)
        self._redirgrp.set_attr("label", label)

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
        if position <= ticks[0]:
            return 0
        elif position >= ticks[-1]:
            return len(ticks) - 1

        ticks = np.array(ticks)
        pidxs = np.searchsorted(ticks, position, side="right") - 1
        return int(pidxs)

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

    def __init__(self, data_array, index):
        nixfile = data_array.file
        super(SetDimension, self).__init__(nixfile, data_array, index)

    @classmethod
    def create_new(cls, data_array, index):
        newdim = cls(data_array, index)
        newdim._set_dimension_type(DimensionType.Set)
        return newdim

    @property
    def labels(self):
        labels = tuple(self._h5group.get_data("labels"))
        if len(labels) and isinstance(labels[0], bytes):
            labels = tuple(label.decode() for label in labels)
        return labels

    @labels.setter
    def labels(self, labels):
        dt = util.vlen_str_dtype
        self._h5group.write_data("labels", labels, dtype=dt)


class DataFrameDimension(Dimension):

    def __init__(self, data_array, index):
        nixfile = data_array.file
        super(DataFrameDimension, self).__init__(nixfile, data_array, index)

    @classmethod
    def create_new(cls, data_array, index, data_frame, column):
        """
        Create a new Dimension that points to a DataFrame

        :param data_array: The DataArray this Dimension belongs to

        :param parent: The H5Group for the dimensions

        :param data_frame: the referenced DataFrame for this Dimension

        :param column: the index of a column in the DataFrame that the
        Dimension will reference (optional)

        :return: The new DataFrameDimension
        """
        newdim = cls(data_array, index)
        newdim.data_frame = data_frame
        newdim.column_idx = column
        newdim._set_dimension_type(DimensionType.DataFrame)
        return newdim

    def get_unit(self, index=None):
        """
        Get the unit of the Dimension.  If an index is specified,
        it will return the unit of the column in the referenced DataFrame at
        that index.

        :param index: Index of the needed column
        :type index: int

        :return: Unit of the specified column
        :rtype: str or None
        """
        if index is None:
            if self.column_idx is None:
                raise ValueError("No default column index is set "
                                 "for this Dimension. Please supply one")
            else:
                idx = self.column_idx
        else:
            idx = index
        unit = None
        if self.data_frame.units is not None:

            unit = self.data_frame.units[idx]
        return unit

    def get_ticks(self, index=None):
        """
        Get the ticks of the Dimension from the referenced DataFrame.
        If an index is specified, it will return the values of the column
        in the referenced DataFrame at that index.

        :param index: Index of the needed column
        :type index: int

        :return: values in the specified column
        :rtype: numpy.ndarray
        """
        if index is None:
            if self.column_idx is None:
                raise ValueError("No default column index is set "
                                 "for this Dimension. Please supply one")
            else:
                idx = self.column_idx
        else:
            idx = index
        df = self.data_frame
        ticks = df[df.column_names[idx]]
        return ticks

    def get_label(self, index=None):
        """
        Get the label of the Dimension. If an index is specified,
         it will return the name of the column in the referenced
         DataFrame at that index.
        :param index: Index of the referred column
        :type index: int or None

        :return: the header of the specified column or the name of DataFrame
        if index is None
        :rtype: str
        """
        if index is None:
            if self.column_idx is None:
                label = self.data_frame.name
            else:
                label = self.data_frame.column_names[self.column_idx]
        else:
            label = self.data_frame.column_names[index]
        return label

    @property
    def data_frame(self):
        dfname = self._h5group.get_by_pos(0).name
        grp = self._h5group.open_group(dfname)
        nixblock = self._parent._parent
        nixfile = self._file
        df = DataFrame(nixfile, nixblock, grp)
        return df

    @data_frame.setter
    def data_frame(self, df):
        self._h5group.create_link(df, "data_frame")

    @property
    def column_idx(self):
        colidx = self._h5group.get_attr("column_idx")
        return colidx

    @column_idx.setter
    def column_idx(self, col):
        self._h5group.set_attr("column_idx", col)
