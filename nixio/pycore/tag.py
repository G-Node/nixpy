# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity_with_sources import EntityWithSources
from . import util


class Tag(EntityWithSources):

    def __init__(self, h5obj):
        super(Tag, self).__init__(h5obj)
        # TODO: Validate data containers

    @classmethod
    def _create_new(cls, parent, name, type_, position):
        newentity = super(Tag, cls)._create_new(parent, name, type_)
        # TODO: Make data containers
        return newentity

    def _add_reference_by_id(self):
        pass

    def _has_reference_by_id(self):
        pass

    def _reference_count(self):
        pass

    def _get_reference_by_id(self):
        pass

    def _get_reference_by_pos(self):
        pass

    def _delete_reference_by_id(self):
        pass

    def create_feature(self):
        pass

    def _has_feature_by_id(self):
        pass

    def _feature_count(self):
        pass

    def _get_feature_by_id(self):
        pass

    def _get_feature_by_pos(self):
        pass

    def _delete_feature_by_id(self):
        pass

    def retrieve_data(self):
        pass

    def retrieve_feature_data(self):
        pass
