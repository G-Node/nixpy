# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

import sys

import nix.util.find as finders
from nix.core import Section
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList

from nix.file import SectionProxyList

class PropertyProxyList(ProxyList):

    def __init__(self, obj):
        super(PropertyProxyList, self).__init__(obj, "_property_count", "_get_property_by_id_or_name",
                                                "_get_property_by_pos", "_delete_property_by_id")

class SectionMixin(Section):

    class __metaclass__(Inject, Section.__class__):
        pass

    def find_sections(self, filtr=lambda _ : True, limit=sys.maxint):
        """
        Get all child sections recursively.

        This method traverses the trees of all sections. The traversal
        is accomplished via breadth first and can be limited in depth. On each node or
        section a filter is applied. If the filter returns true the respective section
        will be added to the result list.
        By default a filter is used that accepts all sections.

        :param filtr: A filter function
        :type filtr:  function
        :param limit: The maximum depth of traversal
        :type limit:  int

        :returns: A list containing the matching sections.
        :rtype: list of Section
        """
        return finders._find_sections(self, filtr, limit)

    def find_related(self, filtr=lambda _ : True):
        """
        Get all related sections of this section.

        The result can be filtered. On each related section a filter is applied. If the filter
        returns true the respective section will be added to the result list. By default a filter
        is used that accepts all sections.

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
        A property providing all child sections of a section. Child sections can be accessed by
        index or by their id. Sections can also be deleted: if a section is deleted, all its
        properties and child sections are removed from the file too.
        Adding new sections is achieved using the create_section method. This is a read-only
        attribute.

        :type: ProxyList of Section
        """
        if not hasattr(self, "_sections"):
            setattr(self, "_sections", SectionProxyList(self))
        return self._sections

    @property
    def properties(self):
        """
        A property containing all Property entities associated with the section. Properties can
        be accessed by index of via their id. Properties can be deleted from the list. Adding
        new properties is done using the create_property method. This is a read-only attribute.

        :type: ProxyList of Property
        """
        if not hasattr(self, "_properties"):
            setattr(self, "_properties", PropertyProxyList(self))
        return self._properties

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False

    def _get_property_by_id_or_name(self, ident):
        p = self._get_property_by_id(ident)
        if p is None and self.has_property_with_name(ident):
            p = self.get_property_with_name(ident)
        return p
