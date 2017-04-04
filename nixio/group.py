# Copyright (c) 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nixio.util.proxy_list import RefProxyList


class DataArrayProxyList(RefProxyList):

    def __init__(self, obj):
        super(DataArrayProxyList, self).__init__(
            obj, "_data_array_count", "_get_data_array_by_id",
            "_get_data_array_by_pos", "_delete_data_array_by_id",
            "_add_data_array_by_id"
        )


class TagProxyList(RefProxyList):

    def __init__(self, obj):
        super(TagProxyList, self).__init__(
            obj, "_tag_count", "_get_tag_by_id",
            "_get_tag_by_pos", "_delete_tag_by_id",
            "_add_tag_by_id"
        )


class MultiTagProxyList(RefProxyList):

    def __init__(self, obj):
        super(MultiTagProxyList, self).__init__(
            obj, "_multi_tag_count", "_get_multi_tag_by_id",
            "_get_multi_tag_by_pos", "_delete_multi_tag_by_id",
            "_add_multi_tag_by_id"
        )


class GroupMixin(object):

    @property
    def data_arrays(self):
        """
        A property containing all data arrays referenced by the group.
        Referenced data arrays can be obtained by index or their id. References
        can be removed from the list, removing a referenced DataArray will not
        remove it from the file. New references can be added using the append
        method of the list.
        This is a read only attribute.

        :type: DataArrayProxyList of DataArray
        """
        if not hasattr(self, "_data_arrays"):
            setattr(self, "_data_arrays", DataArrayProxyList(self))
        return self._data_arrays

    @property
    def tags(self):
        """
        A property containing all tags referenced by the group. Tags can be
        obtained by index or their id. Tags can be removed from the list,
        removing a referenced Tag will not remove it from the file.
        New Tags can be added using the append method of the list.
        This is a read only attribute.

        :type: TagProxyList of Tags
        """
        if not hasattr(self, "_tags"):
            setattr(self, "_tags", TagProxyList(self))
        return self._tags

    @property
    def multi_tags(self):
        """
        A property containing all MultiTags referenced by the group. MultiTags
        can be obtained by index or their id. Tags can be removed from the
        list, removing a referenced MultiTag will not remove it from the file.
        New MultiTags can be added using the append method of the list.
        This is a read only attribute.

        :type: MultiTagProxyList of MultiTags
        """
        if not hasattr(self, "_multi_tags"):
            setattr(self, "_multi_tags", MultiTagProxyList(self))
        return self._multi_tags
