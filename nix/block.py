from __future__ import absolute_import

from nix.core import Block
from nix.util.inject import Inject


class BlockMixin(Block):

    class __metaclass__(Inject, Block.__class__):
        pass

    def test(self):
        print 'success!'
