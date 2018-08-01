# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from .tag import BaseTag, FeatureContainer
from .container import LinkContainer
from .feature import Feature
from .source_link_container import SourceLinkContainer
from .data_array import DataArray
from .data_view import DataView
from .link_type import LinkType
from .exceptions import (OutOfBounds, IncompatibleDimensions,
                         UninitializedEntity)
from .section import Section


class MultiTag(BaseTag):

    def __init__(self, nixparent, h5group):
        super(MultiTag, self).__init__(nixparent, h5group)
        self._sources = None
        self._references = None
        self._features = None

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
        if "positions" not in self._h5group:
            raise RuntimeError("MultiTag.positions: DataArray not found!")
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

    @property
    def references(self):
        """
        A property containing all data arrays referenced by the tag. Referenced
        data arrays can be obtained by index or their id. References can be
        removed from the list, removing a referenced DataArray will not remove
        it from the file. New references can be added using the append method
        of the list.
        This is a read only attribute.

        :type: LinkContainer of DataArray
        """
        if self._references is None:
            self._references = LinkContainer("references", self, DataArray,
                                             self._parent.data_arrays)
        return self._references

    @property
    def features(self):
        """
        A property containing all features of the tag. Features can be obtained
        via their index or their id. Features can be deleted from the list.
        Adding new features to the multitag is done using the create_feature
        method. This is a read only attribute.

        :type: Container of Feature.
        """
        if self._features is None:
            self._features = FeatureContainer("features", self, Feature)
        return self._features

    def _get_slice(self, data, index):
        offset, count = self._get_offset_and_count(data, index)
        sl = tuple(slice(o, o+c) for o, c in zip(offset, count))
        return sl

    def _calc_data_slices(self, data, index):
        positions = self.positions
        extents = self.extents

        pos_size = positions.data_extent if positions else tuple()
        ext_size = extents.data_extent if extents else tuple()

        if not positions or index >= pos_size[0]:
            raise OutOfBounds("Index out of bounds of positions!")

        if extents and index >= ext_size[0]:
            raise OutOfBounds("Index out of bounds of extents!")

        incdim_exception = IncompatibleDimensions(
                "Number of dimensions in positions does not match "
                "dimensionality of data",
                "MultiTag._calc_data_slices"
            )

        if len(pos_size) == 1 and len(data.dimensions) != 1:
            raise incdim_exception

        if len(pos_size) > 1 and pos_size[1] > len(data.dimensions):
            raise incdim_exception

        if (extents and len(ext_size) > 1 and
                ext_size[1] > len(data.dimensions)):
            raise incdim_exception

        dimpos = positions[index, 0:len(data.dimensions)]
        units = self.units
        starts, stops = list(), list()
        for idx in range(dimpos.size):
            dim = data.dimensions[idx]
            unit = None
            if idx <= len(units) and len(units):
                unit = units[idx]
            starts.append(self._pos_to_idx(dimpos.item(idx), unit, dim))

        if extents:
            extent = extents[index, 0:len(data.dimensions)]
            for idx in range(extent.size):
                dim = data.dimensions[idx]
                unit = None
                if idx <= len(units) and len(units):
                    unit = units[idx]
                stop = self._pos_to_idx(dimpos.item(idx) + extent[idx],
                                        unit, dim)
                minstop = starts[idx] + 1
                stops.append(max(stop, minstop))
        else:
            stops = [start+1 for start in starts]

        return tuple(slice(start, stop) for start, stop in zip(starts, stops))

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
        slices = self._calc_data_slices(ref, posidx)

        if not self._slices_in_data(ref, slices):
            raise OutOfBounds("References data slice out of the extent of the "
                              "DataArray!")
        return DataView(ref, slices)

    def retrieve_feature_data(self, posidx, featidx):
        if len(self.features) == 0:
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
            slices = self._calc_data_slices(da, posidx)
            if not self._slices_in_data(da, slices):
                raise OutOfBounds("Requested data slice out of the extent "
                                  "of the Feature!")
            return DataView(da, slices)
        elif feat.link_type == LinkType.Indexed:
            if posidx > da.data_extent[0]:
                raise OutOfBounds("Position is larger than the data stored "
                                  "in the Feature!")
            slices = [slice(posidx, posidx+1)]
            slices.extend(slice(0, stop) for stop in da.data_extent[1:])

            if not self._slices_in_data(da, slices):
                OutOfBounds("Requested data slice out of the extent of the "
                            "Feature!")
            return DataView(da, slices)
        # For untagged return the full data
        slices = tuple(slice(0, stop) for stop in da.data_extent)
        return DataView(da, slices)

    @property
    def sources(self):
        """
        A property containing all Sources referenced by the MultiTag. Sources
        can be obtained by index or their id. Sources can be removed from the
        list, but removing a referenced Source will not remove it from the
        file. New Sources can be added using the append method of the list.
        This is a read only attribute.
        """
        if self._sources is None:
            self._sources = SourceLinkContainer(self)
        return self._sources

    # metadata
    @property
    def metadata(self):
        """

        Associated metadata of the entity. Sections attached to the entity via
        this attribute can provide additional annotations. This is an optional
        read-write property, and can be None if no metadata is available.

        :type: Section
        """
        if "metadata" in self._h5group:
            return Section(None, self._h5group.open_group("metadata"))
        else:
            return None

    @metadata.setter
    def metadata(self, sect):
        if not isinstance(sect, Section):
            raise TypeError("{} is not of type Section".format(sect))
        self._h5group.create_link(sect, "metadata")

    @metadata.deleter
    def metadata(self):
        if "metadata" in self._h5group:
            self._h5group.delete("metadata")
