# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import warnings
import numpy as np
from IPython import embed

from .tag import BaseTag, SliceMode
from .container import LinkContainer
from .source_link_container import SourceLinkContainer
from .data_array import DataArray
from .data_view import DataView
from .link_type import LinkType
from .exceptions import (OutOfBounds, IncompatibleDimensions,
                         UninitializedEntity)
from .section import Section


class MultiTag(BaseTag):

    @classmethod
    def create_new(cls, nixfile, nixparent, h5parent, name, type_, positions):
        newentity = super(MultiTag, cls).create_new(nixfile, nixparent,
                                                    h5parent, name, type_)
        newentity.positions = positions
        return newentity

    @property
    def positions(self):
        """
        The positions defined by the tag. This is a read-write property.

        :type: nixio.DataArray
        """
        if "positions" not in self._h5group:
            raise RuntimeError("MultiTag.positions: DataArray not found!")
        return DataArray(self.file, self._parent,
                         self._h5group.open_group("positions"))

    @positions.setter
    def positions(self, da):
        if da is None:
            raise TypeError("MultiTag.positions cannot be None.")
        if "positions" in self._h5group:
            del self._h5group["positions"]
        self._h5group.create_link(da, "positions")
        if self.file.auto_update_timestamps:
            self.force_updated_at()

    @property
    def extents(self):
        """
        The extents defined by the tag. This is an optional read-write
        property and may be set to None.

        :type: nixio.DataArray or None
        """
        if "extents" in self._h5group:
            return DataArray(self.file, self._parent,
                             self._h5group.open_group("extents"))
        return None

    @extents.setter
    def extents(self, da):
        if da is None:
            del self._h5group["extents"]
        else:
            self._h5group.create_link(da, "extents")
        if self.file.auto_update_timestamps:
            self.force_updated_at()

    @property
    def references(self):
        """
        A property containing all data arrays referenced by the tag. Referenced
        data arrays can be obtained by index or their id. References can be
        removed from the list, removing a referenced DataArray will not remove
        it from the file. New references can be added using the append method
        of the list.
        This is a read only attribute.

        :type: nixio.LinkContainer of nixio.DataArray
        """
        if self._references is None:
            self._references = LinkContainer("references", self, DataArray,
                                             self._parent.data_arrays)
        return self._references

    def _calc_data_slices_mtag(self, data, index, stop_rule):
        positions = self.positions
        extents = self.extents
        if not positions or index >= positions.shape[0]:
            raise OutOfBounds("Index out of bounds of positions!")

        if extents and index >= extents.shape[0]:
            raise OutOfBounds("Index out of bounds of extents!")

        if extents and positions.data_extent != extents.data_extent:
            raise IncompatibleDimensions("Number of dimensions in position and extent do not match",
                                         "MultiTag._calc_data_slices_mtag")

        if len(positions.shape) == 1:
            # 1D positions => multiple positions for 1D data
            # Convert to 2D => each position an array with len 1
            positions = np.array([p for p in positions])

        if extents and len(extents.shape) == 1:
            # 1D extents => multiple extents for 1D data
            # Convert to 2D => each extent an array with len 1
            extents = np.array([e for e in extents])

        position = positions[index]
        extent = None
        if extents is not None and len(extents) > 0:
            extent = extents[index]
        return self._calc_data_slices(data, position, extent, stop_rule)

    def retrieve_data(self, posidx, refidx):
        msg = ("Call to deprecated method MultiTag.retrieve_data. "
               "Use MultiTag.tagged_data instead.")
        warnings.warn(msg, category=DeprecationWarning)
        return self.tagged_data(posidx, refidx)

    def tagged_data(self, posidx, refidx, stop_rule=SliceMode.Exclusive):
        references = self.references
        positions = self.positions
        extents = self.extents
        if len(references) == 0:
            raise OutOfBounds("There are no references in this multitag!")

        if (posidx >= positions.data_extent[0] or
                extents and posidx >= extents.data_extent[0]):
            raise OutOfBounds("Index out of bounds of positions or extents!")

        ref = references[refidx]

        slices = self._calc_data_slices_mtag(ref, posidx, stop_rule)
        return DataView(ref, slices)

    def retrieve_feature_data(self, posidx, featidx):
        msg = ("Call to deprecated method MultiTag.retrieve_feature_data. "
               "Use MultiTag.feature_data instead.")
        warnings.warn(msg, category=DeprecationWarning)
        return self.feature_data(posidx, featidx)

    def feature_data(self, posidx, featidx, stop_rule=SliceMode.Exclusive):
        if len(self.features) == 0:
            msg = "There are no features associated with this tag!"
            raise OutOfBounds(msg)

        try:
            feat = self.features[featidx]
        except KeyError:
            feat = None
            for feature in self.features:
                if feature.data.name == featidx or feature.data.id == featidx:
                    feat = feature
                    break
            if feat is None:
                raise
        data = feat.data
        if data is None:
            raise UninitializedEntity()
        if feat.link_type == LinkType.Tagged:
            slices = self._calc_data_slices_mtag(data, posidx, stop_rule)
            if not self._slices_in_data(data, slices):
                raise OutOfBounds("Requested data slice out of the extent "
                                  "of the Feature!")
            return DataView(data, slices)
        if feat.link_type == LinkType.Indexed:
            if posidx > data.data_extent[0]:
                raise OutOfBounds("Position is larger than the data stored "
                                  "in the Feature!")
            slices = [slice(posidx, posidx + 1)]
            slices.extend(slice(0, stop) for stop in data.data_extent[1:])

            if not self._slices_in_data(data, slices):
                msg = "Requested data slice out of the extent of the Feature!"
                raise OutOfBounds(msg)
            return DataView(data, slices)
        # For untagged return the full data
        slices = tuple(slice(0, stop) for stop in data.data_extent)
        return DataView(data, slices)

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

        :type: nixio.Section
        """
        if "metadata" in self._h5group:
            return Section(self.file, None, self._h5group.open_group("metadata"))
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
