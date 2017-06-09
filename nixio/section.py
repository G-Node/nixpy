# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import functools
from sys import maxsize as maxint
from operator import attrgetter
from collections import Sequence

from .entity import NamedEntity
from .property import Property
from .util import find as finders
from .util.proxy_list import ProxyList
from .value import Value
from . import util
from . import exceptions


class SectionProxyList(ProxyList):

    def __init__(self, obj):
        super(SectionProxyList, self).__init__(obj, "_section_count",
                                               "_get_section_by_id",
                                               "_get_section_by_pos",
                                               "_delete_section_by_id")


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
        else:
            return getattr(self.section, item)


class PropertyProxyList(ProxyList):

    def __init__(self, obj):
        super(PropertyProxyList, self).__init__(obj,
                                                "_property_count",
                                                "_get_property_by_id_or_name",
                                                "_get_property_by_pos",
                                                "_delete_property_by_id")


class Section(NamedEntity):

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
        except KeyError:
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
        A property providing all child sections of a section. Child sections
        can be accessed by index or by their id. Sections can also be deleted:
        if a section is deleted, all its properties and child sections are
        removed from the file too. Adding new sections is achieved using the
        create_section method.
        This is a read-only attribute.

        :type: ProxyList of Section
        """
        if not hasattr(self, "_sections"):
            setattr(self, "_sections", SectionProxyList(self))
        return self._sections

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
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
        values = list(map(attrgetter('value'), prop.values))
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

        val = list(map(lambda x: x if isinstance(x, Value) else Value(x),
                       data))
        dtypes = functools.reduce(
            lambda x, y: x if y.data_type in x else x + [y.data_type],
            val, [val[0].data_type]
        )
        if len(dtypes) > 1:
            raise ValueError('Not all input values are of the same type')

        if key not in self.props:
            prop = self.create_property(key, dtypes[0])
        else:
            prop = self.props[key]
        prop.values = val

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
        section.  Properties can be accessed by index of via their id.
        Properties can be deleted from the list. Adding new properties is done
        using the create_property method.
        This is a read-only attribute.

        :type: ProxyList of Property
        """
        if not hasattr(self, "_properties_proxy"):
            setattr(self, "_properties_proxy", PropertyProxyList(self))
        return self._properties_proxy

    def _get_property_by_id_or_name(self, ident):
        """
        Helper method that gets a property by id or name
        """
        p = self._get_property_by_id(ident)
        if p is None and self.has_property_by_name(ident):
            p = self.get_property_by_name(ident)
        return p
