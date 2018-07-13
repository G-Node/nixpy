# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import numpy as np

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


class FeatureContainer(Container):
    """
    The FeatureContainer has one minor difference from the regular Container:
    A Feature can be retrieved by the ID or name of the linked DataArray as
    well as the ID of the feature itself.
    """
    def __getitem__(self, item):
        try:
            return Container.__getitem__(self, item)
        except KeyError as ke:
            # item might be the ID of the referenced data; try it as well
            for feat in self:
                if feat.data.id == item or feat.data.name == item:
                    return feat
            raise ke

    def __contains__(self, item):
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
            for u in units:
                util.check_attr_type(u, str)
                u = util.units.sanitizer(u)
                sanitized.append(u)

            dtype = DataType.String
            self._h5group.write_data("units", sanitized, dtype)
            self.force_updated_at()

    def create_feature(self, data, link_type):
        """
        Create a new feature.

        :param data: The data array of this feature.
        :type data: DataArray
        :param link_type: The link type of this feature.
        :type link_type: LinkType

        :returns: The created feature object.
        :rtype: Feature
        """
        features = self._h5group.open_group("features")
        feat = Feature._create_new(self, features, data, link_type)
        return feat

    @staticmethod
    def _slices_in_data(data, slices):
        dasize = data.data_extent
        stops = tuple(sl.stop for sl in slices)
        return np.all(np.less_equal(stops, dasize))

    @staticmethod
    def _pos_to_idx(pos, unit, dim):
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
                        "Cannot apply a position with unit to a SetDimension",
                        "Tag._pos_to_idx"
                    )

            index = dim.index_of(pos * scaling)
        elif dimtype == DimensionType.Set:
            if unit and unit != "none":
                raise IncompatibleDimensions(
                    "Cannot apply a position with unit to a SetDimension",
                    "Tag._pos_to_idx"
                )
            index = np.round(pos)
            nlabels = len(dim.labels)
            if nlabels and index > nlabels:
                raise OutOfBounds("Position is out of bounds in SetDimension",
                                  pos)
        else:  # dimtype == DimensionType.Range:
            if dimunit and unit is not None:
                try:
                    scaling = util.units.scaling(unit, dimunit)
                except InvalidUnit:
                    raise IncompatibleDimensions(
                        "Provided units are not scalable!",
                        "Tag._pos_to_idx"
                    )
            index = dim.index_of(pos * scaling)

        return int(index)


class Tag(BaseTag):

    def __init__(self, nixparent, h5group):
        super(Tag, self).__init__(nixparent, h5group)
        self._sources = None
        self._references = None
        self._features = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, position):
        newentity = super(Tag, cls)._create_new(nixparent, h5parent,
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

    def _calc_data_slices(self, data):
        refslice = list()
        position = self.position
        extent = self.extent
        for idx, (pos, dim) in enumerate(zip(position, data.dimensions)):
            if self.units:
                unit = self.units[idx]
            else:
                unit = None
            start = self._pos_to_idx(pos, unit, dim)
            stop = 0
            if idx < len(extent):
                ext = extent[idx]
                stop = self._pos_to_idx(pos + ext, unit, dim)
            if stop == 0:
                stop = start + 1
            refslice.append(slice(start, stop))
        return tuple(refslice)

    def retrieve_data(self, refidx):
        references = self.references
        position = self.position
        extent = self.extent
        if len(references) == 0:
            raise OutOfBounds("There are no references in this tag!")

        if isinstance(refidx, int) and refidx >= len(references):
            raise OutOfBounds("Reference index out of bounds.")

        ref = references[refidx]
        dimcount = len(ref.dimensions)
        if (len(position) != dimcount) or (len(extent) > 0 and
                                           len(extent) != dimcount):
            raise IncompatibleDimensions(
                "Number of dimensions in position or extent do not match "
                "dimensionality of data",
                "Tag.retrieve_data")

        slices = self._calc_data_slices(ref)
        if not self._slices_in_data(ref, slices):
            raise OutOfBounds("References data slice out of the extent of the "
                              "DataArray!")
        return DataView(ref, slices)

    def retrieve_feature_data(self, featidx):
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
            slices = self._calc_data_slices(da)
            if not self._slices_in_data(da, slices):
                raise OutOfBounds("Requested data slice out of the extent "
                                  "of the Feature!")
            return DataView(da, slices)
        # For untagged and indexed return the full data
        fullslices = tuple(slice(0, stop) for stop in da.shape)
        return DataView(da, fullslices)

    @property
    def references(self):
        """
        A property containing all data arrays referenced by the tag. Referenced
        data arrays can be obtained by index or their id. References can be
        removed from the list, removing a referenced DataArray will not remove
        it from the file. New references can be added using the append method
        of the list.
        This is a read only attribute.

        Link:type: Container of DataArray
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
        Adding new features to the tag is done using the create_feature method.
        This is a read only attribute.

        :type: Container of Feature.
        """
        if self._features is None:
            self._features = FeatureContainer("features", self, Feature)
        return self._features

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
