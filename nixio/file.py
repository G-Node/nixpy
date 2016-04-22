# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function, unicode_literals)

import sys

import nixio.util.find as finders
from nixio.core import File as CPPFile
from nixio.pycore import File as PyFile
from nixio.util.inject import inject
from nixio.util.proxy_list import ProxyList

try:
    from sys import maxint
except:
    from sys import maxsize as maxint


class BlockProxyList(ProxyList):

    def __init__(self, obj):
        super(BlockProxyList, self).__init__(obj, "_block_count", "_get_block_by_id",
                                             "_get_block_by_pos", "_delete_block_by_id")


class SectionProxyList(ProxyList):

    def __init__(self, obj):
        super(SectionProxyList, self).__init__(obj, "_section_count", "_get_section_by_id",
                                               "_get_section_by_pos", "_delete_section_by_id")


class FileMixin(CPPFile, PyFile):

    @staticmethod
    def open(path, mode, backend="hdf5"):
        if backend == "hdf5":
            return CPPFile._open(path, mode)
        elif backend == "h5py":
            return PyFile._open(path, mode)

    @property
    def blocks(self):
        """
        A property containing all blocks of a file. Blocks can be obtained by their id or their
        index. Blocks can be deleted from the list, when a block is deleted all its content
        (data arrays, tags and sources) will be also deleted from the file.
        Adding new Block is done via the crate_block method of File. This is a read-only attribute.

        :type: ProxyList of Block entities.
        """
        if not hasattr(self, "_blocks"):
            setattr(self, "_blocks", BlockProxyList(self))
        return self._blocks

    def find_sections(self, filtr=lambda _ : True, limit=maxint):
        """
        Get all sections and their child sections recursively.

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

    @property
    def sections(self):
        """
        A property containing all root sections of a file. Specific root sections can be obtained
        by their id or their index. Sections can be deleted from this list. Notice: when a section
        is deleted all its child section and properties will be removed too.
        Adding a new Section is done via the crate_section method of File. This is a read-only
        property.

        :type: ProxyList of Section entities.
        """
        if not hasattr(self, "_sections"):
            setattr(self, "_sections", SectionProxyList(self))
        return self._sections


inject((CPPFile, PyFile), dict(FileMixin.__dict__))
