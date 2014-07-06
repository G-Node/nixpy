# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import absolute_import

from nix.core import SimpleTag
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList, RefProxyList


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


class SimpleTagMixin(SimpleTag):

    class __metaclass__(Inject, SimpleTag.__class__):

    @property
    def references(self):
        if not hasattr(self, "_references"):
            setattr(self, "_references", ReferenceProxyList(self))
        return self._references

    @property
    def features(self):
        if not hasattr(self, "_features"):
            setattr(self, "_features", FeatureProxyList(self))
        return self._features
