# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nixio.util.proxy_list import ProxyList, RefProxyList


class ReferenceProxyList(RefProxyList):

    def __init__(self, obj):
        super(ReferenceProxyList, self).__init__(
            obj, "_reference_count", "_get_reference_by_id",
            "_get_reference_by_pos", "_delete_reference_by_id",
            "_add_reference_by_id"
        )


class FeatureProxyList(ProxyList):

    def __init__(self, obj):
        super(FeatureProxyList, self).__init__(
            obj, "_feature_count", "_get_feature_by_id",
            "_get_feature_by_pos", "_delete_feature_by_id"
        )


class TagMixin(object):

    @property
    def references(self):
        """
        A property containing all data arrays referenced by the tag. Referenced
        data arrays can be obtained by index or their id. References can be
        removed from the list, removing a referenced DataArray will not remove
        it from the file. New references can be added using the append method
        of the list.
        This is a read only attribute.

        :type: RefProxyList of DataArray
        """
        if not hasattr(self, "_references"):
            setattr(self, "_references", ReferenceProxyList(self))
        return self._references

    @property
    def features(self):
        """
        A property containing all features of the tag. Features can be obtained
        via their index or their id. Features can be deleted from the list.
        Adding new features to the tag is done using the create_feature method.
        This is a read only attribute.

        :type: ProxyList of Feature.
        """
        if not hasattr(self, "_features"):
            setattr(self, "_features", FeatureProxyList(self))
        return self._features
