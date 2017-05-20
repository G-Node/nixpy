# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

from ..multi_tag import MultiTagMixin
from .tag import BaseTag
from .data_array import DataArray
from .data_view import DataView
from ..link_type import LinkType
from .exceptions import (OutOfBounds, IncompatibleDimensions,
                         UninitializedEntity)


class MultiTag(BaseTag, MultiTagMixin):

    def __init__(self, nixparent, h5group):
        super(MultiTag, self).__init__(nixparent, h5group)

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, positions):
        newentity = super(MultiTag, cls)._create_new(nixparent, h5parent,
                                                     name, type_)
        newentity.positions = positions
        return newentity

    @property
    def positions(self):
        """
        The positions defined by the tag. This is a read-write property.

        :type: DataArray
        """
        return DataArray(self._parent, self._h5group.open_group("positions"))

    @positions.setter
    def positions(self, da):
        if da is None:
            raise TypeError("MultiTag.positions cannot be None.")
        if "positions" in self._h5group:
            del self._h5group["positions"]
        self._h5group.create_link(da, "positions")
        self.force_updated_at()

    @property
    def extents(self):
        """
        The extents defined by the tag. This is an optional read-write
        property and may be set to None.

        :type: DataArray or None
        """
        if "extents" in self._h5group:
            return DataArray(self._parent, self._h5group.open_group("extents"))
        else:
            return None

    @extents.setter
    def extents(self, da):
        if da is None:
            del self._h5group["extents"]
        else:
            self._h5group.create_link(da, "extents")

    def _get_offset_and_count(self, data, index):
        offsets = []
        counts = []
        positions = self.positions
        extents = self.extents

        pos_size = positions.data_extent if positions else tuple()
        ext_size = extents.data_extent if extents else tuple()

        if not positions or index >= pos_size[0]:
            raise OutOfBounds("Index out of bounds of positions!")

        if extents and index >= ext_size[0]:
            raise OutOfBounds("Index out of bounds of extents!")

        if len(pos_size) == 1 and len(data.dimensions) != 1:
            raise IncompatibleDimensions(
                "Number of dimensions in positions does not match "
                "dimensionality of data",
                "MultiTag._get_offset_and_count"
            )

        if len(pos_size) > 1 and pos_size[1] > len(data.dimensions):
            raise IncompatibleDimensions(
                "Number of dimensions in positions does not match "
                "dimensionality of data",
                "MultiTag._get_offset_and_count"
            )

        if (extents and len(ext_size) > 1 and
                ext_size[1] > len(data.dimensions)):
            raise IncompatibleDimensions(
                "Number of dimensions in extents does not match "
                "dimensionality of data",
                "MultiTag._get_offset_and_count"
            )

        offset = positions[index, 0:len(data.dimensions)]
        units = self.units
        for idx in range(offset.size):
            dim = data.dimensions[idx]
            unit = None
            if idx <= len(units) and len(units):
                unit = units[idx]
            offsets.append(self._pos_to_idx(offset.item(idx), unit, dim))

        if extents:
            extent = extents[index, 0:len(data.dimensions)]
            for idx in range(extent.size):
                dim = data.dimensions[idx]
                unit = None
                if idx <= len(units) and len(units):
                    unit = units[idx]
                c = self._pos_to_idx(offset.item(idx) + extent.item(idx),
                                     unit, dim) - offsets[idx]
                counts.append(c if c > 1 else 1)
        else:
            counts = [1]*len(data.dimensions)

        return offsets, counts

    def retrieve_data(self, posidx, refidx):
        references = self.references
        positions = self.positions
        extents = self.extents
        if len(references) == 0:
            raise OutOfBounds("There are no references in this multitag!")

        if (posidx >= positions.data_extent[0] or
                extents and posidx >= extents.data_extent[0]):
            raise OutOfBounds("Index out of bounds of positions or extents!")

        ref = references[refidx]
        dimcount = len(ref.dimensions)
        if len(positions.data_extent) == 1 and dimcount != 1:
            raise IncompatibleDimensions(
                "Number of dimensions in position or extent do not match "
                "dimensionality of data",
                "MultiTag.retrieve_data")
        if len(positions.data_extent) > 1:
            if (positions.data_extent[1] > dimcount or
                    extents and extents.data_extent[1] > dimcount):
                raise IncompatibleDimensions(
                    "Number of dimensions in position or extent do not match "
                    "dimensionality of data",
                    "MultiTag.retrieve_data")
        offset, count = self._get_offset_and_count(ref, posidx)

        if not self._position_and_extent_in_data(ref, offset, count):
            raise OutOfBounds("References data slice out of the extent of the "
                              "DataArray!")
        return DataView(ref, count, offset)

    def retrieve_feature_data(self, posidx, featidx):
        if self._feature_count() == 0:
            raise OutOfBounds(
                "There are no features associated with this tag!"
            )

        try:
            feat = self.features[featidx]
        except KeyError:
            feat = None
            for f in self.features:
                if f.data.name == featidx or f.data.id == featidx:
                    feat = f
                    break
            if feat is None:
                raise
        da = feat.data
        if da is None:
            raise UninitializedEntity()
        if feat.link_type == LinkType.Tagged:
            offset, count = self._get_offset_and_count(da, posidx)
            if not self._position_and_extent_in_data(da, offset, count):
                raise OutOfBounds("Requested data slice out of the extent "
                                  "of the Feature!")
            return DataView(da, count, offset)
        elif feat.link_type == LinkType.Indexed:
            if posidx > da.data_extent[0]:
                raise OutOfBounds("Position is larger than the data stored "
                                  "in the Feature!")
            offset = [0] * len(da.data_extent)
            offset[0] = posidx
            count = list(da.data_extent)
            count[0] = 1

            if not self._position_and_extent_in_data(da, offset, count):
                OutOfBounds("Requested data slice out of the extent of the "
                            "Feature!")
            return DataView(da, count, offset)
        # For untagged return the full data
        count = da.data_extent
        offset = (0,) * len(count)
        return DataView(da, count, offset)
