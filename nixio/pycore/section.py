# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from collections import Sequence
import numpy as np

from .entity import NamedEntity
from ..section import SectionMixin
from .util import util
from . import Property
from . import exceptions
from ..value import Value, DataType


class Section(NamedEntity, SectionMixin):

    def __init__(self, h5group):
        super(Section, self).__init__(h5group)

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Section, cls)._create_new(parent, name, type_)
        return newentity

    # Section
    def create_section(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        sections = self._h5group.open_group("sections", True)
        if name in sections:
            raise exceptions.DuplicateName("create_section")
        sec = Section._create_new(sections, name, type_)
        return sec

    def _get_section_by_id(self, id_or_name):
        sections = self._h5group.open_group("sections")
        return Section(sections.get_by_id_or_name(id_or_name))

    def _get_section_by_pos(self, pos):
        sections = self._h5group.open_group("sections")
        return Section(sections.get_by_pos(pos))

    def _delete_section_by_id(self, id_or_name):
        sections = self._h5group.open_group("sections")
        sections.delete(id_or_name)

    def _section_count(self):
        return len(self._h5group.open_group("sections"))

    # Property
    def create_property(self, name, value):
        properties = self._h5group.open_group("properties", True)
        if name in properties:
            raise exceptions.DuplicateName("create_property")
        if isinstance(value, type):
            dtype = value
            value = Value(0)
        else:
            if isinstance(value, Sequence):
                dtype = value[0].data_type
            else:
                dtype = value.data_type
        prop = Property._create_new(properties, name, dtype)
        prop.value = value
        return prop

    def has_property_by_name(self, name):
        return self._h5group.has_by_id(name)

    def _get_property_by_id(self, id_or_name):
        properties = self._h5group.open_group("properties")
        return Property(properties.get_by_id_or_name(id_or_name))

    def _get_property_by_pos(self, pos):
        properties = self._h5group.open_group("properties")
        return Property(properties.get_by_pos(pos))

    def _delete_property_by_id(self, id_or_name):
        properties = self._h5group.open_group("properties")
        properties.delete(id_or_name)

    def _property_count(self):
        return len(self._h5group.open_group("properties"))

    @property
    def parent(self):
        h5parent = self._h5group.parent
        if h5parent.group.name == "/metadata":
            # Top level section
            return None
        else:
            return Section(h5parent.parent)

    @property
    def link(self):
        if "link" not in self._h5group:
            return None
        else:
            return Section(self._h5group["link"])

    @link.setter
    def link(self, id_or_sec):
        if isinstance(id_or_sec, Section):
            id = id_or_sec.id
        else:
            id = id_or_sec
        # TODO: Complete the link setter
        pass

    def inherited_properties(self):
        properties = [Property(h5prop)
                      for h5prop in self._h5group["properties"].values()]
        if self.link:
            properties.append(self.link.inherited_properties)
        return properties

    @property
    def mapping(self):
        return self._h5group.get_attr("mapping")

    @mapping.setter
    def mapping(self, m):
        util.check_attr_type(m, str)
        self._h5group.set_attr("mapping", m)

    @property
    def repository(self):
        return self._h5group.get_attr("repository")

    @repository.setter
    def repository(self, r):
        util.check_attr_type(r, str)
        self._h5group.set_attr("repository", r)

