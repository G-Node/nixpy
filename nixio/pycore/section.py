# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

from collections import Sequence

from ..value import Value
from ..section import SectionMixin
from .entity import NamedEntity
from .property import Property
from . import util
from . import exceptions


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

    def _delete_section_by_id(self, id_):
        sections = self._h5group.open_group("sections")
        sections.delete(id_)

    def _section_count(self):
        return len(self._h5group.open_group("sections"))

    # Property
    def create_property(self, name, value):
        properties = self._h5group.open_group("properties", True)
        if name in properties:
            raise exceptions.DuplicateName("create_property")
        if isinstance(value, type):
            dtype = value
            values = [Value(0)]
        else:
            if isinstance(value, Sequence):
                dtype = value[0].data_type
                values = value
            else:
                dtype = value.data_type
                values = [value]
        prop = Property._create_new(properties, name, dtype)
        prop.values = values
        return prop

    def has_property_by_name(self, name):
        properties = self._h5group.open_group("properties")
        return properties.has_by_id(name)

    def get_property_by_name(self, name):
        properties = self._h5group.open_group("properties")
        try:
            p = Property(properties.get_by_name(name))
        except ValueError:
            p = None
        return p

    def _get_property_by_id(self, id_or_name):
        properties = self._h5group.open_group("properties")
        return Property(properties.get_by_id_or_name(id_or_name))

    def _get_property_by_pos(self, pos):
        properties = self._h5group.open_group("properties")
        return Property(properties.get_by_pos(pos))

    def _delete_property_by_id(self, id_):
        properties = self._h5group.open_group("properties")
        properties.delete(id_)

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
            return Section(self._h5group.open_group("link"))

    @link.setter
    def link(self, id_or_sec):
        if id_or_sec is None:
            self._h5group.delete("link")
        if isinstance(id_or_sec, Section):
            sec = id_or_sec
        else:
            rootsec = Section(self._h5group.h5root)
            sec = rootsec.find_sections(filtr=lambda x: x.id == id_or_sec)

        self._h5group.create_link(sec, "link")

    def inherited_properties(self):
        properties = self._h5group.open_group("properties")
        inhprops = [Property(h5prop) for h5prop in properties]
        if self.link:
            inhprops.append(self.link.inherited_properties)
        return inhprops

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

