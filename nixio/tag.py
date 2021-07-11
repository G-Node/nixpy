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
from six import string_types

from .entity import Entity
from .source_link_container import SourceLinkContainer
from .container import Container, LinkContainer

from .datatype import DataType
from .data_array import DataArray
from .data_view import DataView
from .feature import Feature
from .exceptions import (OutOfBounds, IncompatibleDimensions,
                         UninitializedEntity, InvalidUnit)
from .dimension_type import DimensionType
from .link_type import LinkType
from . import util
from .section import Section
from .dimensions import SliceMode


class FeatureContainer(Container):
    """
    The FeatureContainer has one minor difference from the regular Container:
    A Feature can be retrieved by the ID or name of the linked DataArray as
    well as the ID of the feature itself.
    """
    def __getitem__(self, item):
        try:
            return Container.__getitem__(self, item)
        except KeyError as exc:
            # item might be the ID of the referenced data; try it as well
            for feat in self:
                if feat.data.id == item or feat.data.name == item:
                    return feat
            raise exc

    def __contains__(self, item):
        if isinstance(item, Feature):
            item = item.id
        if not Container.__contains__(self, item):
            # check if it contains a Feature whose data matches 'item'
            for feat in self:
                if feat.data.id == item or feat.data.name == item:
                    return True
            return False
        return True


class BaseTag(Entity):
    """
    Base class for Tag and MultiTag
    """
    def __init__(self, nixfile, nixparent, h5group):
        super(BaseTag, self).__init__(nixfile, nixparent, h5group)
        self._sources = None
        self._references = None
        self._features = None

    @property
    def units(self):
        """
        Property containing the units of the tag. The tag must provide a
        unit for each dimension of the position or extent vector.
        This is a read-write property.

        :type: list of str
        """
        return tuple(u.decode() if isinstance(u, bytes) else u
                     for u in self._h5group.get_data("units"))

    @units.setter
    def units(self, units):
        if not units:
            if self._h5group.has_data("units"):
                del self._h5group["units"]
        else:
            sanitized = []
            for unit in units:
                util.check_attr_type(unit, str)
                unit = util.units.sanitizer(unit)
                sanitized.append(unit)

            dtype = DataType.String
            self._h5group.write_data("units", sanitized, dtype)
        if self.file.auto_update_timestamps:
            self.force_updated_at()

    def create_feature(self, data, link_type):
        """
        Create a new feature.

        :param data: The data array of this feature.
        :type data: nixio.DataArray
        :param link_type: The link type of this feature.
        :type link_type: nixio.LinkType

        :returns: The created feature object.
        :rtype: nixio.Feature
        """
        if isinstance(link_type, string_types):
            link_type = link_type.lower()
        link_type = LinkType(link_type)
        features = self._h5group.open_group("features")
        feat = Feature.create_new(self.file, self, features, data, link_type)
        return feat

    def _calc_data_slices(self, data, position, extent, stop_rule):
        refslice = list()
        if not self.units:
            units = [None] * len(data.dimensions)
        else:
            units = self.units

        for idx, dim in enumerate(data.dimensions):
            scaling = 1.0
            if idx < len(position):
                start_pos = position[idx]
                start_pos, scaling = self._scale_position(start_pos, units[idx], dim)
                if extent is not None and idx < len(extent):
                    stop_pos = extent[idx]
                    stop_pos *= scaling
                    stop_pos += start_pos
                    slice_mode = stop_rule if extent[idx] > 0.0 else SliceMode.Inclusive
                else:
                    stop_pos = start_pos
                    slice_mode = SliceMode.Inclusive
                range_indices = dim.range_indices(start_pos, stop_pos, slice_mode)
                refslice.append(range_indices if range_indices is None else slice(range_indices[0], range_indices[1] + 1))
            else:  # no position, we take the whole slice for this dimension
                start_index = 0
                stop_index = data.shape[idx]
                refslice.append(slice(start_index, stop_index))

        return tuple(refslice)

    @staticmethod
    def _slices_in_data(data, slices):
        if slices is None or not all(slices):
            return False
        dasize = data.data_extent
        stops = tuple(sl.stop for sl in slices)
        return np.all(np.less_equal(stops, dasize))

    @staticmethod
    def _scale_position(pos, unit, dim):
        dimtype = dim.dimension_type
        if dimtype == DimensionType.Set:
            dimunit = None
        else:
            dimunit = dim.unit
        scaling = 1.0
        if dimtype == DimensionType.Set:
            if unit and unit != "none":
                raise IncompatibleDimensions(
                    "Cannot apply a position with unit to a SetDimension",
                    "Tag._pos_to_idx"
                )
        else:
            if dimunit is None and unit is not None:
                raise IncompatibleDimensions(
                    "Units of position and SampledDimension "
                    "must both be given!",
                    "Tag._pos_to_idx"
                )
            elif dimunit is not None and unit is not None:
                try:
                    scaling = util.units.scaling(unit, dimunit)
                except InvalidUnit:
                    raise IncompatibleDimensions(
                        "Cannot scale Tag unit {} to match dimension unit {}".format(unit, dimunit),
                        "Tag._pos_to_idx"
                    )
        return pos * scaling, scaling

    @staticmethod
    def _pos_to_idx(pos, unit, dim, mode):
        dimtype = dim.dimension_type
        if dimtype == DimensionType.Set:
            dimunit = None
        else:
            dimunit = dim.unit
        scaling = 1.0
        if dimtype == DimensionType.Sample:
            if not dimunit and unit is not None:
                raise IncompatibleDimensions(
                    "Units of position and SampledDimension "
                    "must both be given!",
                    "Tag._pos_to_idx"
                )
            if dimunit and unit is not None:
                try:
                    scaling = util.units.scaling(unit, dimunit)
                except InvalidUnit:
                    raise IncompatibleDimensions(
                        "Cannot scale Tag unit {} to match dimension unit {}".format(unit, dimunit),
                        "Tag._pos_to_idx"
                    )
            index = dim.index_of(pos * scaling, mode)
        elif dimtype == DimensionType.Set:
            if unit and unit != "none":
                raise IncompatibleDimensions(
                    "Cannot apply a position with unit to a SetDimension",
                    "Tag._pos_to_idx"
                )
            index = dim.index_of(pos, mode)
        else:  # dimtype == DimensionType.Range:
            if dimunit and unit is not None:
                try:
                    scaling = util.units.scaling(unit, dimunit)
                except InvalidUnit:
                    raise IncompatibleDimensions(
                        "Cannot scale Tag unit {} to match dimension unit {}".format(unit, dimunit),
                        "Tag._pos_to_idx"
                    )
            index = dim.index_of(pos * scaling, mode)

        return int(index)

    @property
    def features(self):
        """
        A property containing all features. Features can be obtained
        via their index or their ID. Features can be deleted from the list.
        Adding new features is done using the create_feature method.
        This is a read only attribute.

        :type: Container of nixio.Feature.
        """
        if self._features is None:
            self._features = FeatureContainer("features", self.file,
                                              self, Feature)
        return self._features


class Tag(BaseTag):

    @classmethod
    def create_new(cls, nixfile, nixparent, h5parent, name, type_, position):
        newentity = super(Tag, cls).create_new(nixfile, nixparent, h5parent,
                                               name, type_)
        newentity.position = position
        return newentity

    @property
    def position(self):
        """
        The position defined by the tag. This is a read-write property.

        :type: list of float
        """
        return tuple(self._h5group.get_data("position"))

    @position.setter
    def position(self, pos):
        if pos is None or len(pos) == 0:
            if self._h5group.has_data("position"):
                del self._h5group["position"]
        else:
            dtype = DataType.Double
            self._h5group.write_data("position", pos, dtype)
        if self.file.auto_update_timestamps:
            self.force_updated_at()

    @property
    def extent(self):
        """
        The extent defined by the tag. This is an optional read-write
        property and may be set to None.

        :type: list of float
        """
        return tuple(self._h5group.get_data("extent"))

    @extent.setter
    def extent(self, ext):
        if ext is None or len(ext) == 0:
            if self._h5group.has_data("extent"):
                del self._h5group["extent"]
        else:
            dtype = DataType.Double
            self._h5group.write_data("extent", ext, dtype)
        if self.file.auto_update_timestamps:
            self.force_updated_at()

    def retrieve_data(self, refidx):
        msg = ("Call to deprecated method Tag.retrieve_data. "
               "Use Tag.tagged_data instead.")
        warnings.warn(msg, category=DeprecationWarning)
        return self.tagged_data(refidx)

    def tagged_data(self, refidx, stop_rule=SliceMode.Exclusive):
        references = self.references
        position = self.position
        extent = self.extent
        if len(references) == 0:
            raise OutOfBounds("There are no references in this tag!")

        if isinstance(refidx, int) and refidx >= len(references):
            raise OutOfBounds("Reference index out of bounds.")

        ref = references[refidx]
        if extent and len(position) != len(extent):
            raise IncompatibleDimensions(
                "Number of dimensions in position and extent "
                "do not match ", extent)

        slices = self._calc_data_slices(ref, self.position, self.extent, stop_rule)
        if not self._slices_in_data(ref, slices):
            raise OutOfBounds("References data slice out of the extent of the "
                              "DataArray!")
        return DataView(ref, slices)

    def retrieve_feature_data(self, featidx):
        msg = ("Call to deprecated method Tag.retrieve_feature_data. "
               "Use Tag.feature_data instead.")
        warnings.warn(msg, category=DeprecationWarning)
        return self.feature_data(featidx)

    def feature_data(self, featidx, stop_rule=SliceMode.Exclusive):
        if len(self.features) == 0:
            raise OutOfBounds("There are no features associated with this tag!")

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
            slices = self._calc_data_slices(data, self.position, self.extent, stop_rule)
            if not self._slices_in_data(data, slices):
                raise OutOfBounds("Requested data slice out of the extent "
                                  "of the Feature!")
            return DataView(data, slices)
        # For untagged and indexed return the full data
        fullslices = tuple(slice(0, stop) for stop in data.shape)
        return DataView(data, fullslices)

    @property
    def references(self):
        """
        A property containing all data arrays referenced by the tag. Referenced
        data arrays can be obtained by index or their id. References can be
        removed from the list, removing a referenced DataArray will not remove
        it from the file. New references can be added using the append method
        of the list.
        This is a read only attribute.

        :type: Container of nixio.DataArray
        """
        if self._references is None:
            self._references = LinkContainer("references", self, DataArray,
                                             self._parent.data_arrays)
        return self._references

    @property
    def sources(self):
        """
        A property containing all Sources referenced by the Tag. Sources
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
