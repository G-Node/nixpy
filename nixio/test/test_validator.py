from __future__ import (absolute_import, division, print_function)
import nixio as nix
import numpy as np
import os
import unittest
from .tmp import TempDir
from ..validate import Validate

file = nix.File.open('neoraw1.nix', 'a')

val = Validate(file)
print(val)

class TestValidate (unittest.TestCase):


    def setUp(self):
        self.tmpdir = TempDir("validatetest")
        self.testfilename = os.path.join(self.tmpdir.path, "validatetest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("blk1", "blk")
        self.block1 = self.file.create_block("blk2", "blk2")
        for blk in self.block, self.block1:
            # blk.create_section("metadata", "md")  # create metatdata
            for i in range(2):
                blk.create_group("grp{}".format(i), "groups")
            for i in range(4):
                blk.create_data_array("da{}".format(i), "data_arrays",
                                      dtype="float",
                                      data=(1 + np.random.random((10, 10))))
            for i in range(4):
                blk.create_tag("tag{}".format(i), "tags",
                               np.random.random((10, 10)))
            for i in range(4):
                blk.create_multi_tag("mt{}".format(i), "multi_tags",
                                     blk.data_arrays[i])
        self.validator = Validate(self.file)
        self.validator.form_dict()


    def tearDown(self):
        self.file.close()
        self.tmpdir.cleanup()

    def test_check_file(self):
        assert self.validator.check_file() is None
        self.file.force_created_at(0)
        assert self.validator.check_file()['files'] == ["date is not set!"]


    def test_check_blocks(self):
        block = self.block
        assert self.validator.errors['blocks'][0]['blk_err'] == []
        block._h5group.set_attr("name", None)
        assert self.validator.check_blocks(block, 0)\
            ['blocks'][0]['blk_err'] == ['Name of some Block is missing']
        block._h5group.set_attr("type", None)
        self.validator.check_blocks(block, 0)
        assert self.validator.errors['blocks'][0]['blk_err'] == ['Type of some Block is '
                                            'missing', 'Name of some Block is missing']

    def test_check_groups(self):
        pass
