# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import NamedEntity
from ..section import SectionMixin
from .util import util
from . import Property
from . import exceptions


class Section(NamedEntity, SectionMixin):

    def __init__(self, h5obj):
        super(Section, self).__init__(h5obj)

    @classmethod
    def _create_new(cls, parent, name, type_):
        newentity = super(Section, cls)._create_new(parent, name, type_)
        newentity._h5obj.create_group("sections")
        newentity._h5obj.create_group("properties")
        return newentity

    # Section
    def create_section(self, name, type_):
        util.check_entity_name_and_type(name, type_)
        sections = self._h5obj["sections"]
        if name in sections:
            raise exceptions.DuplicateName("create_section")
        sec = Section._create_new(sections, name, type_)
        return sec

    def _get_section_by_id(self, id_or_name):
        return Section(util.id_or_name_getter(self._h5obj["sections"],
                                              id_or_name))

    def _get_section_by_pos(self, pos):
        return Section(util.pos_getter(self._h5obj["sections"], pos))

    def _delete_section_by_id(self, id_or_name):
        util.deleter(self._h5obj["sections"], id_or_name)

    def _section_count(self):
        return len(self._h5obj["sections"])

    # Property
    def create_property(self, name, dtype):
        properties = self._h5obj["properties"]
        if name in properties:
            raise exceptions.DuplicateName("create_property")
        prop = Property._create_new(properties)
        return prop

    def has_property_by_name(self, name):
        return name in self._h5obj["properties"]

    def _get_property_by_id(self, id_or_name):
        return Property(util.id_or_name_getter(self._h5obj["properties"],
                                               id_or_name))

    def _get_property_by_pos(self, pos):
        return Property(util.pos_getter(self._h5obj["properties"], pos))

    def _delete_property_by_id(self, id_or_name):
        util.deleter(self._h5obj["properties"], id_or_name)

    def _property_count(self):
        return len(self._h5obj["properties"])

    @property
    def parent(self):
        h5parent = self._h5obj.parent
        if h5parent.name == "/metadata":
            # Top level section
            return None
        else:
            return Section(h5parent.parent)

    @property
    def link(self):
        if "link" not in self._h5obj:
            return None
        else:
            return Section(self._h5obj["link"])

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
                      for h5prop in self._h5obj["properties"].values()]
        if self.link:
            properties.append(self.link.inherited_properties)
        return properties

util.create_h5props(Section, ("mapping", "repository"), (str, str))
