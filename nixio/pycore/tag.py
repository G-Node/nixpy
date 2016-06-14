# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import numpy as np

from .entity_with_sources import EntityWithSources
from ..tag import TagMixin
from ..value import DataType
from .data_array import DataArray


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
        pass

    def _has_feature_by_id(self, id_or_name):
        features = self._h5group.open_group("features")
        return features.has_by_id(id_or_name)

    def _feature_count(self):
        return len(self._h5group.open_group("features"))

    def _get_feature_by_id(self, id_or_name):
        features = self._h5group.open_group("features")
        return features.get_by_id(id_or_name)

    def _get_feature_by_pos(self, pos):
        features = self._h5group.open_group("features")
        return features.get_by_pos(pos)

    def _delete_feature_by_id(self, id_or_name):
        features = self._h5group.open_group("features")
        features.delete_by_id(id_or_name)

    def retrieve_data(self):
        pass

    def retrieve_feature_data(self):
        pass

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
