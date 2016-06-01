# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from . import util
from .entity_with_sources import EntityWithSources


class DataArray(EntityWithSources):

    def __init__(self, h5obj):
        super(DataArray, self).__init__(h5obj)
        # TODO: Validate data containers

    @classmethod
    def _create_new(cls, parent, name, type_, data):
        newentity = super(DataArray, cls)._create_new(parent, name, type_)
        # TODO: Make data containers
        return newentity

    def create_set_dimension(self):
        pass

    def create_sampled_dimension(self):
        pass

    def create_range_dimension(self):
        pass

    def append_set_dimension(self):
        pass

    def append_sampled_dimension(self):
        pass

    def append_range_dimension(self):
        pass

    def append_alias_range_dimension(self):
        pass

    def _dimension_count(self):
        pass

    def _delete_dimension_by_pos(self, index):
        pass

    def _get_dimension_by_pos(self, index):
        pass


class DataSet(object):
    pass
