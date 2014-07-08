# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import Section
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList

from nix.file import SectionProxyList

class PropertyProxyList(ProxyList):

    def __init__(self, obj):
        super(PropertyProxyList, self).__init__(obj, "_property_count", "_get_property_by_id",
                                                "_get_property_by_pos", "_delete_property_by_id")
# TODO find and find_related section method
# TODO proxy list with names
# TODO proxy list with inherited properties
class SectionMixin(Section):

    class __metaclass__(Inject, Section.__class__):
        pass

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
