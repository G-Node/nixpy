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

    def _linked_group(self):
        return self._h5group.get_by_pos(0)

    @property
    def linked_data(self):
        grp = self._linked_group()
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
    def values(self):
        """
        Returns the values (vector or column) from the linked data object
        (DataArray or DataFrame) specified by the LinkDimension's index.
        """
        data = self.linked_data
        if self._data_object_type == "DataArray":
            dimindex = list(self.index)
            # replace -1 with slice(None)
            dimindex[dimindex.index(-1)] = slice(None)
            return data[tuple(dimindex)]
        elif self._data_object_type == "DataFrame":
            return tuple(row[self.index] for row in data)
        else:
            raise RuntimeError("Invalid DataObjectType attribute found in "
                               "DimensionLink")

    @property
    def unit(self):
        """
        Returns the unit from the linked data object (DataArray or DataFrame)
        specified by the LinkDimension's index.
        """
        lobj = self._linked_group()
        if self._data_object_type == "DataArray":
            return lobj.get_attr("unit")
        elif self._data_object_type == "DataFrame":
            return lobj.get_attr("units")[self.index]
        else:
            raise RuntimeError("Invalid DataObjectType attribute found in "
                               "DimensionLink")

    @unit.setter
    def unit(self, unit):
        """
        Sets the unit of the linked data object.
        """
        lobj = self._linked_group()
        if self._data_object_type == "DataArray":
            lobj.set_attr("unit", unit)
        elif self._data_object_type == "DataFrame":
            units = list(lobj.get_attr("units"))
            units[self.index] = unit
            lobj.set_attr("units", units)
        else:
            raise RuntimeError("Invalid DataObjectType attribute found in "
                               "DimensionLink")

    @property
    def label(self):
        """
        Returns the label of the linked data object:
        For DataArray links, returns the label.
        For DataFrame links, returns the name of the column specified by the
        LinkDimension's index.
        """
        lobj = self._linked_group()
        if self._data_object_type == "DataArray":
            return lobj.get_attr("label")
        elif self._data_object_type == "DataFrame":
            col_dts = lobj.group["data"].dtype
            return col_dts.names[self.index]
        else:
            raise RuntimeError("Invalid DataObjectType attribute found in "
                               "DimensionLink")

    @label.setter
    def label(self, label):
        """
        Sets the label of the linked data objet.
        """
        lobj = self._linked_group()
        if self._data_object_type == "DataArray":
            lobj.set_attr("label", label)
        elif self._data_object_type == "DataFrame":
            raise RuntimeError("The label of a Dimension linked to a "
                               "DataFrame column cannot be modified")
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

        invalid_idx_msg = (
            "Invalid linked DataArray index: "
            "One of the values must be -1, indicating the relevant vector. "
            "Negative indexing is not supported."
        )
        if index.count(-1) != 1 or sum(idx < 0 for idx in index) != 1:
            # TODO: Add link to relevant docs
            raise ValueError(invalid_idx_msg)

        if self.has_link:
            self.remove_link()
        DimensionLink.create_new(self._file, self, self._h5group,
                                 data_array, "DataArray", index)

    def link_data_frame(self, data_frame, index):
        if not 0 <= index < len(data_frame.columns):
            raise OutOfBounds("DataFrame index is out of bounds", index)
        if self.has_link:
            self.remove_link()
        DimensionLink.create_new(self._file, self, self._h5group,
                                 data_frame, "DataFrame", index)

    def remove_link(self):
        if not self.has_link:
            raise RuntimeError("Dimension has no link")
        self._h5group.delete("link", False)

    @property
    def has_link(self):
        """
        Return True if this Dimension links to a data object
        (DataArray or DataFrame).
        Read-only property.
        """
        if "link" in self._h5group:
            return True
        return False

    @property
    def dimension_link(self):
        """
        If the dimension has a DimensionLink to a data object, returns the
        DimensionLink object, otherwise returns None.
        """
        if self.has_link:
            link = self._h5group.get_by_name("link")
            return DimensionLink(self._file, self, link)
        return None

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

    def index_of(self, position, leq=True):
        """
        Returns the index of a certain position in the dimension.

        :param position: The position.
        :param leq: Less or Equal mode (default True).
                    Whether to return the index if it matches the position exactly.
                    If 'leq' is False and the position matches an index, it returns the previous index.
                    This can be used to maintain consistency with cases when the position falls between indexes, in
                    which case the previous valid index is returned.

        :returns: The matching index
        :rtype: int
        """
        offset = self.offset if self.offset else 0
        sample = self.sampling_interval
        scaled_position = (position - offset) / sample
        if scaled_position < 0:
            raise IndexError("Position is out of bounds of this dimension!")

        index = int(scaled_position)
        if not scaled_position.is_integer():
            # inexact position: floored regardless of leq
            return index

        # exact position: return if leq, otherwise previous
        if leq:
            return index

        return index-1

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
    def unit(self, unit):
        util.check_attr_type(unit, str)
        self._h5group.set_attr("unit", unit)

    @property
    def offset(self):
        return self._h5group.get_attr("offset")

    @offset.setter
    def offset(self, offset):
        util.check_attr_type(offset, Number)
        self._h5group.set_attr("offset", offset)

    def link_data_array(self, *_):
        raise RuntimeError("SampledDimension does not support linking")

    def link_data_frame(self, *_):
        raise RuntimeError("SampledDimension does not support linking")


class RangeDimension(Dimension):

    def __init__(self, data_array, index):
        nixfile = data_array.file
        super(RangeDimension, self).__init__(nixfile, data_array, index)

    def link_data_array(self, data_array, index):
        if "ticks" in self._h5group:
            # delete ticks to replace with link
            self._h5group.delete("ticks", False)
        super(RangeDimension, self).link_data_array(data_array, index)

    def link_data_frame(self, data_frame, index):
        if "ticks" in self._h5group:
            # delete ticks to replace with link
            self._h5group.delete("ticks", False)
        super(RangeDimension, self).link_data_frame(data_frame, index)

    @classmethod
    def create_new(cls, data_array, index, ticks):
        newdim = cls(data_array, index)
        newdim._set_dimension_type(DimensionType.Range)
        if ticks is not None:
            newdim._h5group.write_data("ticks", ticks, dtype=DataType.Double)
        return newdim

    @property
    def ticks(self):
        if self.has_link:
            ticks = self.dimension_link.values
        else:
            ticks = self._h5group.get_data("ticks")
        return tuple(ticks)

    @ticks.setter
    def ticks(self, ticks):
        if np.any(np.diff(ticks) < 0):
            raise ValueError("Ticks are not given in an ascending order.")
        if self.has_link:
            # unlick object and set ticks
            self.remove_link()
        self._h5group.write_data("ticks", ticks)

    @property
    def label(self):
        if self.has_link:
            return self.dimension_link.label
        return self._h5group.get_attr("label")

    @label.setter
    def label(self, label):
        util.check_attr_type(label, str)
        if self.has_link:
            self.dimension_link.label = label
        else:
            self._h5group.set_attr("label", label)

    @property
    def unit(self):
        if self.has_link:
            return self.dimension_link.unit
        return self._h5group.get_attr("unit")

    @unit.setter
    def unit(self, unit):
        util.check_attr_type(unit, str)
        if self.has_link:
            self.dimension_link.unit = unit
        else:
            self._h5group.set_attr("unit", unit)

    def index_of(self, position, leq=True):
        """
        Returns the index of a certain position in the dimension.

        :param position: The position.
        :param leq: Less or Equal mode (default True).
                    Whether to return the index if it matches the position exactly.
                    If 'leq' is False and the position matches an index, it returns the previous index.
                    This can be used to maintain consistency with cases when the position falls between indexes, in
                    which case the previous valid index is returned.

        :returns: The matching index
        :rtype: int
        """
        ticks = self.ticks
        if position <= ticks[0]:
            return 0

        ticks = np.array(ticks)
        if leq:
            return np.where(ticks <= position)[0][-1]

        return np.where(ticks < position)[0][-1]

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
        if self.has_link:
            labels = self.dimension_link.values
        else:
            labels = self._h5group.get_data("labels")

        if len(labels) and isinstance(labels[0], bytes):
            labels = tuple(label.decode() for label in labels)

        return tuple(labels)

    @labels.setter
    def labels(self, labels):
        if self.has_link:
            raise RuntimeError("The labels of a SetDimension linked to a "
                               "data object cannot be modified")
        dt = util.vlen_str_dtype
        self._h5group.write_data("labels", labels, dtype=dt)
