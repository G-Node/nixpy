# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)

import nixio.util.find as finders
from nixio.util.proxy_list import ProxyList
import numpy as np

try:
    from sys import maxint
except:
    from sys import maxsize as maxint


class SourceProxyList(ProxyList):

    def __init__(self, obj):
        super(SourceProxyList, self).__init__(obj, "_source_count",
                                              "_get_source_by_id",
                                              "_get_source_by_pos",
                                              "_delete_source_by_id")


class DataArrayProxyList(ProxyList):

    def __init__(self, obj):
        super(DataArrayProxyList, self).__init__(obj, "_data_array_count",
                                                 "_get_data_array_by_id",
                                                 "_get_data_array_by_pos",
                                                 "_delete_data_array_by_id")


class MultiTagProxyList(ProxyList):

    def __init__(self, obj):
        super(MultiTagProxyList, self).__init__(obj, "_multi_tag_count",
                                                "_get_multi_tag_by_id",
                                                "_get_multi_tag_by_pos",
                                                "_delete_multi_tag_by_id")


class TagProxyList(ProxyList):

    def __init__(self, obj):
        super(TagProxyList, self).__init__(obj, "_tag_count", "_get_tag_by_id",
                                           "_get_tag_by_pos",
                                           "_delete_tag_by_id")


class GroupProxyList(ProxyList):

    def __init__(self, obj):
        super(GroupProxyList, self).__init__(obj, "_group_count",
                                             "_get_group_by_id",
                                             "_get_group_by_pos",
                                             "_delete_group_by_id")


class BlockMixin(object):

    def create_data_array(self, name, array_type,
                          dtype=None, shape=None, data=None):
        """
        Create a new data array for this block. Either ``shape``
        or ``data`` must be given. If both are given their shape must agree.
        If ``dtype`` is not specified it will default to 64-bit floating
        points.

        :param name: The name of the data array to create.
        :type name: str
        :param array_type: The type of the data array.
        :type array_type: str
        :param dtype: Which data-type to use for storage
        :type dtype:  :class:`numpy.dtype`
        :param shape: Layout (dimensionality and extent)
        :type shape: tuple of int or long
        :param data: Data to write after storage has been created
        :type data: array-like data

        :returns: The newly created data array.
        :rtype: :class:`~nixio.DataArray`
        """

        if data is None:
            if shape is None:
                raise ValueError("Either shape and or data must not be None")
            if dtype is None:
                dtype = 'f8'
        else:
            data = np.ascontiguousarray(data)
            if dtype is None:
                dtype = data.dtype
            if shape is not None:
                if shape != data.shape:
                    raise ValueError("Shape must equal data.shape")
            else:
                shape = data.shape
        da = self._create_data_array(name, array_type, dtype, shape)
        if data is not None:
            da.write_direct(data)
        return da

    def find_sources(self, filtr=lambda _: True, limit=None):
        """
        Get all sources in this block recursively.

        This method traverses the tree of all sources in the block. The
        traversal is accomplished via breadth first and can be limited in
        depth.  On each node or source a filter is applied. If the filter
        returns true the respective source will be added to the result list.
        By default a filter is used that accepts all sources.

        :param filtr: A filter function
        :type filtr:  function
        :param limit: The maximum depth of traversal
        :type limit:  int

        :returns: A list containing the matching sources.
        :rtype: list of Source
        """
        if limit is None:
            limit = maxint
        return finders._find_sources(self, filtr, limit)

    @property
    def sources(self):
        """
        A property containing all sources of a block. Sources can be obtained
        via their index or by their id. Sources can be deleted from the list.
        Adding sources is done using the Blocks create_source method.
        This is a read only attribute.

        :type: ProxyList of Source entities.
        """
        if not hasattr(self, "_sources"):
            setattr(self, "_sources", SourceProxyList(self))
        return self._sources

    @property
    def multi_tags(self):
        """
        A property containing all multi tags of a block. MultiTag entities can
        be obtained via their index or by their id. Tags can be deleted from
        the list. Adding tags is done using the Blocks create_multi_tag method.
        This is a read only attribute.

        :type: ProxyList of MultiTag entities.
        """
        if not hasattr(self, "_multi_tags"):
            setattr(self, "_multi_tags", MultiTagProxyList(self))
        return self._multi_tags

    @property
    def tags(self):
        """
        A property containing all tags of a block. Tag entities can be obtained
        via their index or by their id. Tags can be deleted from the list.
        Adding tags is done using the Blocks create_tag method.
        This is a read only attribute.

        :type: ProxyList of Tag entities.
        """
        if not hasattr(self, "_tags"):
            setattr(self, "_tags", TagProxyList(self))
        return self._tags

    @property
    def data_arrays(self):
        """
        A property containing all data arrays of a block. DataArray entities
        can be obtained via their index or by their id. Data arrays can be
        deleted from the list. Adding a data array is done using the Blocks
        create_data_array method.
        This is a read only attribute.

        :type: ProxyList of DataArray entities.
        """
        if not hasattr(self, "_data_arrays"):
            setattr(self, "_data_arrays", DataArrayProxyList(self))
        return self._data_arrays

    @property
    def groups(self):
        """
        A property containing all groups of a block. Group entities can be
        obtained via their index or by their id. Groups can be deleted from the
        list. Adding a Group is done using the Blocks create_group method.
        This is a read only attribute.

        :type: ProxyList of Group entities.
        """
        if not hasattr(self, "_groups"):
            setattr(self, "_groups", GroupProxyList(self))
        return self._groups

    def __eq__(self, other):
        """
        Two blocks are considered equal when they have the same id.
        """
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
