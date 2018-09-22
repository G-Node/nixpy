# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
try:
    from sys import maxint
except ImportError:
    from sys import maxsize as maxint
from collections import Sequence, Iterable
from six import string_types

from .container import Container, SectionContainer
from .datatype import DataType
from .entity import Entity
from .property import Property
from .util import find as finders
from . import util
from . import exceptions


class S(object):
    def __init__(self, section_type, section=None):
        self.section_type = section_type
        self.section = section

    def __setitem__(self, key, value):
        self.section[key] = value

    def __setattr__(self, key, value):
        if key in ['section_type', 'section']:
            object.__setattr__(self, key, value)
        else:
            setattr(self.section, key, value)

    def __getattribute__(self, item):
        if item in ['section_type', 'section']:
            return object.__getattribute__(self, item)

        return getattr(self.section, item)


class Section(Entity):

    def __init__(self, nixparent, h5group):
        super(Section, self).__init__(nixparent, h5group)
        self._sec_parent = None
        self._sections = None
        self._properties = None

    @classmethod
    def _create_new(cls, nixparent, h5parent, name, type_, oid=None):
        newentity = super(Section, cls)._create_new(nixparent, h5parent,
                                                    name, type_)
        if util.is_uuid(oid):
            newentity._h5group.set_attr("entity_id", oid)

        return newentity

    # Section
    def create_section(self, name, type_="undefined", oid=None):
        """
        Creates a new subsection that is a child of this section entity.

        :param name: The name of the section to create.
        :type name: str
        :param type_: The type of the section.
        :type type_: str
        :param oid: object id, UUID string as specified in RFC 4122. If no id
                    is provided, an id will be generated and assigned.
        :type oid: str

        :returns: The newly created section.
        :rtype: Section
        """
        util.check_entity_name_and_type(name, type_)
        sections = self._h5group.open_group("sections", True)
        if name in sections:
            raise exceptions.DuplicateName("create_section")
        sec = Section._create_new(self, sections, name, type_, oid)
        sec._sec_parent = self
        return sec

    # Property
    def create_property(self, name, values_or_dtype, oid=None):
        """
        Add a new property to the section.

        :param name: The name of the property to create.
        :type name: str
        :param values_or_dtype: The values of the property or a valid DataType.
        :type values_or_dtype: list of values or a DataType
        :param oid: object id, UUID string as specified in RFC 4122. If no id
                    is provided, an id will be generated and assigned.
        :type oid: str

        :returns: The newly created property.
        :rtype: Property
        """
        vals = values_or_dtype

        properties = self._h5group.open_group("properties", True)
        if name in properties:
            raise exceptions.DuplicateName("create_property")

        # Handle handed in DataType
        if isinstance(vals, type):
            dtype = vals
            vals = []

        # In case of values, make sure boolean value 'False' gets through as
        # well, but ensure that empty values are not allowed, we need a
        # DataType.
        elif vals is None or (isinstance(vals, (Sequence, Iterable)) and
                              not len(vals)):
            raise TypeError(
                "Please provide either a non empty value or a DataType."
            )

        else:
            # Make sure all values are of the same data type
            single_val = vals
            if (isinstance(vals, (Sequence, Iterable)) and
                    not isinstance(vals, string_types)):
                single_val = vals[0]
            else:
                # Make sure the data will always be created with an array.
                vals = [vals]

            # Will raise an error, if the datatype of the first value is not
            # valid.
            dtype = DataType.get_dtype(single_val)

            # Check all values for data type consistency to ensure clean value
            # add. Will raise an exception otherwise.
            for v in vals:
                if DataType.get_dtype(v) != dtype:
                    raise TypeError("Array contains inconsistent values.")

        prop = Property._create_new(self, properties, name, dtype, oid)
        prop.values = vals

        return prop

    @property
    def reference(self):
        return self._h5group.get_attr("reference")

    @reference.setter
    def reference(self, ref):
        util.check_attr_type(ref, str)
        self._h5group.set_attr("reference", ref)

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
            inhprops.extend(self.link.inherited_properties())
        return inhprops

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
        while isinstance(par, Entity):
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

    def find_sections(self, filtr=lambda _: True, limit=None):
        """
        Get all child sections recursively.
        This method traverses the trees of all sections. The traversal is
        accomplished via breadth first and can be limited in depth.
        On each node or section a filter is applied.
        If the filter returns true the respective section will be added to the
        result list.  By default a filter is used that accepts all sections.

        :param filtr: A filter function
        :type filtr:  function
        :param limit: The maximum depth of traversal
        :type limit:  int

        :returns: A list containing the matching sections.
        :rtype: list of Section
        """
        if limit is None:
            limit = maxint
        return finders._find_sections(self, filtr, limit)

    def find_related(self, filtr=lambda _: True):
        """
        Get all related sections of this section.

        The result can be filtered. On each related section a filter is
        applied.  If the filter returns true the respective section will be
        added to the result list. By default a filter is used that accepts all
        sections.

        :param filtr: A filter function
        :type filtr:  function

        :returns: A list containing the matching related sections.
        :rtype: list of Section
        """
        result = []
        if self.parent is not None:
            result = finders._find_sections(self.parent, filtr, 1)
        if self in result:
            del result[result.index(self)]
        result += finders._find_sections(self, filtr, 1)
        return result

    @property
    def sections(self):
        """
        A property providing all child Sections of a Section. Child sections
        can be accessed by name, index, or id. Sections can also be deleted:
        if a Section is deleted, all its properties and child Sections are
        removed from the file too. Adding new Sections is achieved using the
        create_section method.
        This is a read-only attribute.

        :type: Container of Section
        """
        if self._sections is None:
            self._sections = SectionContainer("sections", self, Section)
        return self._sections

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id

        return False

    def __hash__(self):
        """
        overwriting method __eq__ blocks inheritance of __hash__ in Python 3
        hash has to be either explicitly inherited from parent class,
        implemented or escaped
        """
        return hash(self.id)

    def __len__(self):
        return len(self.props)

    def __getitem__(self, key):

        if key not in self.props and key in self.sections:
            return self.sections[key]

        prop = self.props[key]
        values = list(prop.values)
        if len(values) == 1:
            values = values[0]
        return values

    def __delitem__(self, key):
        del self.props[key]

    def __setitem__(self, key, data):

        if isinstance(data, S):
            data.section = self.create_section(key, data.section_type)
            return

        if not isinstance(data, list):
            data = [data]

        if key not in self.props:
            prop = self.create_property(key, data)
        else:
            prop = self.props[key]
            prop.values = data

    def __iter__(self):
        for name, item in self.items():
            yield item

    def items(self):
        for p in self.props:
            yield (p.name, p)
        for s in self.sections:
            yield (s.name, s)

    def __contains__(self, key):
        return key in self.props or key in self.sections

    @property
    def props(self):
        """
        A property containing all Property entities associated with the
        section. Properties can be accessed by name, index, or id.
        Properties can be deleted from the list. Adding new Properties is done
        using the create_property method.
        This is a read-only attribute.

        :type: Container of Property
        """
        if self._properties is None:
            self._properties = Container("properties", self, Property)
        return self._properties
