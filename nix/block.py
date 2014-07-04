# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import Block
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList

class SourceProxyList(ProxyList):

    def __init__(self, obj):
        super(SourceProxyList, self).__init__(obj, "_source_count", "_get_source_by_id",
                                              "_get_source_by_pos", "_delete_source_by_id")


class DataArrayProxyList(ProxyList):

    def __init__(self, obj):
        super(DataArrayProxyList, self).__init__(obj, "_data_array_count", "_get_data_array_by_id",
                                                 "_get_data_array_by_pos", "_delete_data_array_by_id")


class DataTagProxyList(ProxyList):

    def __init__(self, obj):
        super(DataTagProxyList, self).__init__(obj, "_data_tag_count", "_get_data_tag_by_id",
                                               "_get_data_tag_by_pos", "_delete_data_tag_by_id")


class SimpleTagProxyList(ProxyList):

    def __init__(self, obj):
        super(SimpleTagProxyList, self).__init__(obj, "_simple_tag_count", "_get_simple_tag_by_id",
                                                 "_get_simple_tag_by_pos", "_delete_simple_tag_by_id")


class BlockMixin(Block):

    class __metaclass__(Inject, Block.__class__):
        # this injects all members and the doc into nix.core.Block
        pass

    @property
    def sources(self):
        """
        A property containing all sources of a block. Sources can be obtained via their index or by their id.
        Sources can be deleted from the list. Adding sources is done using the Blocks create_source method.
        This is a read only attribute.

        :type: ProxyList of Source entities.
        """
        if not hasattr(self, "_sources"):
            setattr(self, "_sources", SourceProxyList(self))
        return self._sources

    @property
    def data_tags(self):
        """
        A property containing all data tags of a block. DataTag entities can be obtained via their index or by their id.
        Tags can be deleted from the list. Adding tags is done using the Blocks create_data_tag method.
        This is a read only attribute.

        :type: ProxyList of DataTag entities.
        """
        if not hasattr(self, "_data_tags"):
            setattr(self, "_data_tags", DataTagProxyList(self))
        return self._data_tags

    @property
    def simple_tags(self):
        """
        A property containing all simple tags of a block. SimpleTag entities can be obtained via their index or by their id.
        Tags can be deleted from the list. Adding tags is done using the Blocks create_simple_tag method.
        This is a read only attribute.

        :type: ProxyList of SimpleTag entities.
        """
        if not hasattr(self, "_simple_tags"):
            setattr(self, "_simple_tags", SimpleTagProxyList(self))
        return self._simple_tags

    @property
    def data_arrays(self):
        """
        A property containing all data arrays of a block. DataArray entities can be obtained via their index or by their id.
        Data arrays can be deleted from the list. Adding a data array is done using the Blocks create_data_array method.
        This is a read only attribute.

        :type: ProxyList of DataArray entities.
        """
        if not hasattr(self, "_data_arrays"):
            setattr(self, "_data_arrays", DataArrayProxyList(self))
        return self._data_arrays

    def __eq__(self, other):
        """
        Two blocks are considered equal when they have the same id
        """
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False
