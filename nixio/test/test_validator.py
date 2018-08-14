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
        self.testing_block = self.file.create_block("blk1", "blk")
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
        block = self.testing_block
        assert self.validator.check_blocks(block, 0) is None
        block._h5group.set_attr("name", None)
        assert self.validator.check_blocks(block, 0)['blocks'][0]['blk_err'] == ['Name of some Block is missing']
        block._h5group.set_attr("type", None)
        assert self.validator.check_blocks(block, 0)['blocks'][0]['blk_err'] == ['Name of some Block is missing',
                                                   'Type of some Block is missing']

        # not sure if it is test problem or not, somehow the new checklist append to the old checklist and create
        # duplicates, but supposingly in practice no user should use like this without re-starting the whole class

    def test_check_groups(self):
        pass
