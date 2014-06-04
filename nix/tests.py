__author__ = 'gicmo'
import unittest
import nix.core


class TestFile(unittest.TestCase):
    def setUp(self):
        self.nix_file = nix.core.File.open('test.h5')
        assert(self.nix_file.version == '1.0')

    def basic_test(self):
        b = self.nix_file.create_block('foo', 'bar')
        assert(b)
        assert(len(self.nix_file.blocks()) > 0)
        d = b.create_data_array('foo', 'bar')
        assert b
        assert(len(b.data_arrays()) > 0)