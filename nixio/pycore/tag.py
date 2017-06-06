# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

import numpy as np

from .entity_with_sources import EntityWithSources
from ..tag import TagMixin
from ..value import DataType
from .data_array import DataArray
from .data_view import DataView
from .feature import Feature
from .exceptions import (OutOfBounds, IncompatibleDimensions,
                         UninitializedEntity, InvalidUnit)
from ..dimension_type import DimensionType
from ..link_type import LinkType
from . import util


class BaseTag(EntityWithSources):
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
                if not (util.units.is_si(u) or util.units.is_compound(u)
                        or u == "none"):
                    raise InvalidUnit(
                        "{} is not SI or composite of SI units".format(u),
                        "{}.units".format(type(self).__name__)
                    )
                sanitized.append(u)

            dtype = DataType.String
            self._h5group.write_data("units", sanitized, dtype)
            self.force_updated_at()

    def _add_reference_by_id(self, id_or_name):
        if id_or_name not in self._parent.data_arrays:
            cls = type(self).__name__
            raise RuntimeError("{}._add_reference_by_id: "
                               "Reference not found in Block!".format(cls))
        target = self._parent.data_arrays[id_or_name]
        references = self._h5group.open_group("references")
        references.create_link(target, target.id)

    def _has_reference_by_id(self, id_or_name):
        references = self._h5group.open_group("references")
        return references.has_by_id(id_or_name)

    def _reference_count(self):
        return len(self._h5group.open_group("references"))

    def _get_reference_by_id(self, id_or_name):
        references = self._h5group.open_group("references")
        if util.is_uuid(id_or_name):
            id_ = id_or_name
        else:
            id_ = self._parent.data_arrays[id_or_name].id
        return DataArray(self._parent, references.get_by_id(id_))

    def _get_reference_by_pos(self, pos):
        references = self._h5group.open_group("references")
        return DataArray(self, references.get_by_pos(pos))

    def _delete_reference_by_id(self, id_):
        references = self._h5group.open_group("references")
        references.delete(id_)

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

    def _has_feature_by_id(self, id_or_name):
        features = self._h5group.open_group("features")
        return features.has_by_id(id_or_name)

    def _feature_count(self):
        return len(self._h5group.open_group("features"))

    def _get_feature_by_id(self, id_or_name):
        features = self._h5group.open_group("features")
        return Feature(self, features.get_by_id(id_or_name))

    def _get_feature_by_pos(self, pos):
        features = self._h5group.open_group("features")
        return Feature(self, features.get_by_pos(pos))

    def _delete_feature_by_id(self, id_):
        features = self._h5group.open_group("features")
        features.delete(id_)

    @classmethod
    def _position_and_extent_in_data(cls, data, offset, count):
        pos = tuple(np.add(offset, count) - 1)
        return cls._position_in_data(data, pos)

    @staticmethod
    def _position_in_data(data, pos):
        dasize = data.data_extent
        return np.all(np.less(pos, dasize))

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
            index = round(pos)
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


class Tag(BaseTag, TagMixin):

    def __init__(self, nixparent, h5group):
        super(Tag, self).__init__(nixparent, h5group)

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

    def _get_offset_and_count(self, data):
        offset = []
        count = []
        position = self.position
        extent = self.extent
        for idx in range(len(position)):
            dim = data.dimensions[idx]
            pos = position[idx]
            if self.units:
                unit = self.units[idx]
            else:
                unit = None
            o = self._pos_to_idx(position[idx], unit, dim)
            offset.append(o)
            if idx < len(extent):
                ext = extent[idx]
                c = self._pos_to_idx(pos + ext, unit, dim) - o
                count.append(c if c > 1 else 1)
            else:
                count.append(1)
        return tuple(offset), tuple(count)

    def retrieve_data(self, refidx):
        references = self.references
        position = self.position
        extent = self.extent
        if len(references) == 0:
            raise OutOfBounds("There are no references in this tag!")

        if refidx >= len(references):
            raise OutOfBounds("Reference index out of bounds.")

        ref = references[refidx]
        dimcount = len(ref.dimensions)
        if (len(position) != dimcount) or (len(extent) > 0 and
                                           len(extent) != dimcount):
            raise IncompatibleDimensions(
                "Number of dimensions in position or extent do not match "
                "dimensionality of data",
                "Tag.retrieve_data")

        offset, count = self._get_offset_and_count(ref)

        if not self._position_and_extent_in_data(ref, offset, count):
            raise OutOfBounds("References data slice out of the extent of the "
                              "DataArray!")
        return DataView(ref, count, offset)

    def retrieve_feature_data(self, featidx):
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
            offset, count = self._get_offset_and_count(da)
            if not self._position_and_extent_in_data(da, offset, count):
                raise OutOfBounds("Requested data slice out of the extent "
                                  "of the Feature!")
            return DataView(da, count, offset)
        # For untagged and indexed return the full data
        count = da.data_extent
        offset = (0,) * len(count)
        return DataView(da, count, offset)
