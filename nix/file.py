# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import File
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList

class BlockProxyList(ProxyList):

    def __init__(self, obj):
        super(BlockProxyList, self).__init__(obj, "_block_count", "_get_block_by_id",
                                             "_get_block_by_pos", "_delete_block_by_id")


class SectionProxyList(ProxyList):

    def __init__(self, obj):
        super(SectionProxyList, self).__init__(obj, "_section_count", "_get_section_by_id",
                                               "_get_section_by_pos", "_delete_section_by_id")


class FileMixin(File):

    class __metaclass__(Inject, File.__class__):
        pass

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
