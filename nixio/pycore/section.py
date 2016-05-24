# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import NamedEntity


class Section(NamedEntity):

    def __init__(self, h5obj):
        super(Section, self).__init__(h5obj)

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Section, cls)._create_new(parent, name, type_)
        return newentity

    def create_section(self):
        pass

    def _section_count(self):
        pass

    def _get_section_by_id(self):
        pass

    def _get_section_by_pos(self):
        pass

    def _delete_section_by_id(self):
        pass

    def create_property(self):
        pass

    def has_property_by_name(self):
        pass

    def get_property_by_name(self):
        pass

    def _property_count(self):
        pass

    def _get_property_by_id(self):
        pass

    def _get_property_by_pos(self):
        pass

    def _delete_property_by_id(self):
        pass

    def inherited_properties(self):
        pass
