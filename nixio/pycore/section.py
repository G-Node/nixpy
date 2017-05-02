# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

from collections import Sequence

from ..section import SectionMixin
from .entity import NamedEntity
from .property import Property
from . import util
from . import exceptions


class Section(NamedEntity, SectionMixin):

    def __init__(self, nixparent, h5group):
        super(Section, self).__init__(nixparent, h5group)
        self._sec_parent = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_):
        newentity = super(Section, cls)._create_new(nixparent, h5parent,
                                                    name, type_)
        return newentity

    # Section
    def create_section(self, name, type_):
        """
        Creates a new subsection that is a child of this section entity.

        :param name: The name of the section to create.
        :type name: str
        :param type_: The type of the section.
        :type type_: str

        :returns: The newly created section.
        :rtype: Section
        """
        util.check_entity_name_and_type(name, type_)
        sections = self._h5group.open_group("sections", True)
        if name in sections:
            raise exceptions.DuplicateName("create_section")
        sec = Section._create_new(self, sections, name, type_)
        sec._sec_parent = self
        return sec

    def _get_section_by_id(self, id_or_name):
        sections = self._h5group.open_group("sections")
        return Section(self, sections.get_by_id_or_name(id_or_name))

    def _get_section_by_pos(self, pos):
        sections = self._h5group.open_group("sections")
        return Section(self, sections.get_by_pos(pos))

    def _delete_section_by_id(self, id_):
        sections = self._h5group.open_group("sections")
        sections.delete(id_)

    def _section_count(self):
        return len(self._h5group.open_group("sections"))

    # Property
    def create_property(self, name, values):
        """
        Add a new property to the section.

        :param name: The name of the property to create.
        :type name: str
        :param values: The values of the property.
        :type values: list of Value

        :returns: The newly created property.
        :rtype: Property
        """
        properties = self._h5group.open_group("properties", True)
        if name in properties:
            raise exceptions.DuplicateName("create_property")
        if isinstance(values, type):
            dtype = values
            values = []
        else:
            if isinstance(values, Sequence):
                dtype = values[0].data_type
            else:
                dtype = values.data_type
                values = [values]
        prop = Property._create_new(self, properties, name, dtype)
        prop.values = values
        return prop

    def has_property_by_name(self, name):
        """
        Checks whether a section has a property with a certain name.

        :param name: The name to check.
        :type name: str

        :returns: True if the section has a property with the given name,
                  False otherwise.
        :rtype: bool
        """
        properties = self._h5group.open_group("properties")
        return properties.has_by_id(name)

    def get_property_by_name(self, name):
        """
        Get a property by its name.

        :param name: The name to check.
        :type name: str

        :returns: The property with the given name.
        :rtype: Property
        """
        properties = self._h5group.open_group("properties")
        try:
            p = Property(self, properties.get_by_name(name))
        except ValueError:
            p = None
        return p

    def _get_property_by_id(self, id_or_name):
        properties = self._h5group.open_group("properties")
        return Property(self, properties.get_by_id_or_name(id_or_name))

    def _get_property_by_pos(self, pos):
        properties = self._h5group.open_group("properties")
        return Property(self, properties.get_by_pos(pos))

    def _delete_property_by_id(self, id_):
        properties = self._h5group.open_group("properties")
        properties.delete(id_)

    def _property_count(self):
        return len(self._h5group.open_group("properties"))

    @property
    def link(self):
        """
        Link to another section. If a section is linked to another section,
        the linking section inherits all properties from the target section.
        This is an optional read-write property and may be set to None.

        :type: Section
        """
        if "link" not in self._h5group:
            return None
        else:
            return Section(self, self._h5group.open_group("link"))

    @link.setter
    def link(self, id_or_sec):
        if id_or_sec is None:
            self._h5group.delete("link")
        if isinstance(id_or_sec, Section):
            sec = id_or_sec
        else:
            rootsec = Section(self, self._h5group.h5root)
            sec = rootsec.find_sections(filtr=lambda x: x.id == id_or_sec)

        self._h5group.create_link(sec, "link")

    def inherited_properties(self):
        properties = self._h5group.open_group("properties")
        inhprops = [Property(self, h5prop) for h5prop in properties]
        if self.link:
            inhprops.append(self.link.inherited_properties())
        return inhprops

    @property
    def mapping(self):
        return self._h5group.get_attr("mapping")

    @mapping.setter
    def mapping(self, m):
        """
        The mapping information of the section.
        This is an optional read-write property and may be set to None.

        :type: str
        """
        util.check_attr_type(m, str)
        self._h5group.set_attr("mapping", m)

    @property
    def repository(self):
        """
        URL to the terminology repository the section is associated with.
        This is an optional read-write property and may be set to None.

        :type: str
        """
        return self._h5group.get_attr("repository")

    @repository.setter
    def repository(self, r):
        util.check_attr_type(r, str)
        self._h5group.set_attr("repository", r)

    @property
    def parent(self):
        """
        The parent section. This is a read-only property. For root sections
        this property is always None.

        Accessing this property can be slow when the metadata tree is large.

        :type: Section
        """
        if self._sec_parent is not None:
            return self._sec_parent
        rootmd = self._h5group.file.open_group("metadata")
        # Assuming most metadata trees are shallow---doing BFS
        sections = [Section(None, sg) for sg in rootmd]
        if self in sections:
            # Top-level section
            return None

        while sections:
            sect = sections.pop(0)
            if self in sect.sections:
                self._sec_parent = sect
                return sect
            sections.extend(sect.sections)

        return None

    @property
    def file(self):
        """
        Root file object.

        :type: File
        """
        par = self._parent
        while isinstance(par, NamedEntity):
            par = par._parent
        return par

    @property
    def referring_objects(self):
        objs = []
        objs.extend(self.referring_blocks)
        objs.extend(self.referring_groups)
        objs.extend(self.referring_data_arrays)
        objs.extend(self.referring_tags)
        objs.extend(self.referring_multi_tags)
        objs.extend(self.referring_sources)
        return objs

    @property
    def referring_blocks(self):
        f = self.file
        return list(blk for blk in f.blocks if blk.metadata.id == self.id)

    @property
    def referring_groups(self):
        f = self.file
        groups = []
        for blk in f.blocks:
            groups.extend(grp for grp in blk.groups
                          if grp.metadata.id == self.id)
        return groups

    @property
    def referring_data_arrays(self):
        f = self.file
        data_arrays = []
        for blk in f.blocks:
            data_arrays.extend(da for da in blk.data_arrays
                               if da.metadata.id == self.id)
        return data_arrays

    @property
    def referring_tags(self):
        f = self.file
        tags = []
        for blk in f.blocks:
            tags.extend(tg for tg in blk.tags
                        if tg.metadata.id == self.id)
        return tags

    @property
    def referring_multi_tags(self):
        f = self.file
        multi_tags = []
        for blk in f.blocks:
            multi_tags.extend(mt for mt in blk.multi_tags
                              if mt.metadata.id == self.id)
        return multi_tags

    @property
    def referring_sources(self):
        f = self.file
        sources = []
        for blk in f.blocks:
            sources.extend(src for src in blk.sources
                           if src.metadata.id == self.id)
        return sources
