# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity_with_sources import EntityWithSources
from ..tag import TagMixin
from ..value import DataType
from .data_array import DataArray
from .feature import Feature
from .exceptions import OutOfBounds, IncompatibleDimensions
from ..dimension_type import DimensionType
from ..link_type import LinkType
from . import util


class DataView(object):

    def __init__(self, da, count, offset):
        self.da = da
        self.count = count
        self.offset = offset

    @property
    def size(self):
        return 1


class Tag(EntityWithSources, TagMixin):

    def __init__(self, h5group):
        super(Tag, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, name, type_, position):
        newentity = super(Tag, cls)._create_new(parent, name, type_)
        newentity.position = position
        return newentity

    def _add_reference_by_id(self, id_or_name):
        references = self._h5group.open_group("references")
        references.add_by_id(id_or_name)

    def _has_reference_by_id(self, id_or_name):
        references = self._h5group.open_group("references")
        return references.has_by_id(id_or_name)

    def _reference_count(self):
        return len(self._h5group.open_group("references"))

    def _get_reference_by_id(self, id_or_name):
        references = self._h5group.open_group("references")
        return DataArray(references.get_by_id(id_or_name))

    def _get_reference_by_pos(self, pos):
        references = self._h5group.open_group("references")
        return references.get_by_pos(pos)

    def _delete_reference_by_id(self, id_or_name):
        references = self._h5group.open_group("references")
        references.delete(id_or_name)

    def create_feature(self, da, link_type):
        features = self._h5group.open_group("features")
        feat = Feature._create_new(features, da, link_type)
        return feat

    def _has_feature_by_id(self, id_or_name):
        features = self._h5group.open_group("features")
        return features.has_by_id(id_or_name)

    def _feature_count(self):
        return len(self._h5group.open_group("features"))

    def _get_feature_by_id(self, id_or_name):
        features = self._h5group.open_group("features")
        return Feature(features.get_by_id(id_or_name))

    def _get_feature_by_pos(self, pos):
        features = self._h5group.open_group("features")
        return Feature(features.get_by_pos(pos))

    def _delete_feature_by_id(self, id_or_name):
        features = self._h5group.open_group("features")
        features.delete(id_or_name)

    def retrieve_data(self, refidx):
        references = self._h5group.open_group("references")
        if len(references) == 0:
            raise OutOfBounds("There are no references in this tag!", 0)

        if refidx >= len(references):
            raise OutOfBounds("Reference index out of bounds.", 0)

        ref = references[refidx]
        dimcount = ref.dimension_count()
        if (len(self.position) != dimcount) or (len(self.extent) > 0 and
                                                len(self.extent) != dimcount):
            raise IncompatibleDimensions(
                "Number of dimensions in position or extent do not match "
                "dimensionality of data",
                "Tag.retrieve_data")

        offset, count = self._get_offset_and_count(ref)
        return DataView(ref, count, offset)

    def retrieve_feature_data(self, featidx):
        # TODO: Errors
        feat = self.features[featidx]
        da = feat.data
        if feat.link_type == LinkType.Tagged:
            offset, count = self._get_offset_and_count(da)
            return DataView(da, count, offset)

        count = da.data_extent
        offset = [0] * len(count)
        return DataView(da, count, offset)

    def _get_offset_and_count(self, data):
        offset = []
        count = []
        for idx in range(len(self.position)):
            dim = data.dimensions[idx]
            pos = self.position[idx]
            if self.units:
                unit = self.units[idx]
            else:
                unit = None
            offset.append(self.pos_to_idx(self.position[idx], unit, dim))
            if idx < len(self.extent):
                ext = self.extent[idx]
                count.append(self.pos_to_idx(pos+ext, unit, dim))
            else:
                count.append(1)
        return offset, count

    @staticmethod
    def pos_to_idx(pos, unit, dim):
        if dim.dimension_type in (DimensionType.Sample, DimensionType.Range):
            # scaling = 1.0
            scaling = util.scaling(unit, dim.unit)
            return dim.index_of(pos * scaling)
        elif dim.dimension_type == DimensionType.Set:
            return round(pos)



    @property
    def units(self):
        return tuple(self._h5group.get_data("units"))

    @units.setter
    def units(self, units):
        if not units:
            if self._h5group.has_data("units"):
                del self._h5group["units"]
        else:
            dtype = DataType.String
            self._h5group.write_data("units", units, dtype)
            self.force_updated_at()

    @property
    def position(self):
        return tuple(self._h5group.get_data("position"))

    @position.setter
    def position(self, pos):
        if not pos:
            if self._h5group.has_data("position"):
                del self._h5group["position"]
        else:
            dtype = DataType.Double
            self._h5group.write_data("position", pos, dtype)

    @property
    def extent(self):
        return tuple(self._h5group.get_data("extent"))

    @extent.setter
    def extent(self, ext):
        if not ext:
            if self._h5group.has_data("extent"):
                del self._h5group["extent"]
        else:
            dtype = DataType.Double
            self._h5group.write_data("extent", ext, dtype)
