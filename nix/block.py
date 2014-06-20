from __future__ import absolute_import

from nix.core import Block
from nix.util.inject import Inject
from nix.util.proxy_list import ProxyList

class SourceProxyList(ProxyList):

    def __init__(self, obj):
        super(SourceProxyList, self).__init__(obj, "_source_count", "_get_source_by_id",
                                              "_get_source_by_pos", "_delete_source_by_id")

class BlockMixin(Block):

    class __metaclass__(Inject, Block.__class__):
        pass

    def test(self, what=""):
        print 'success! ' + what

    @property
    def sources(self):
        return SourceProxyList(self)
