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
        pass

    @property
    def sources(self):
        if not hasattr(self, "_sources"):
            setattr(self, "_sources", SourceProxyList(self))
        return self._sources

    @property
    def data_tags(self):
        if not hasattr(self, "_data_tags"):
            setattr(self, "_data_tags", DataTagProxyList(self))
        return self._data_tags

    @property
    def simple_tags(self):
        if not hasattr(self, "_simple_tags"):
            setattr(self, "_simple_tags", SimpleTagProxyList(self))
        return self._simple_tags

    @property
    def data_arrays(self):
        if not hasattr(self, "_data_arrays"):
            setattr(self, "_data_arrays", DataArrayProxyList(self))
        return self._data_arrays

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False
