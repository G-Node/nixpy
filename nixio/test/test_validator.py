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
        self.block1 = self.file.create_block("blk1", "blk")
        self.block2 = self.file.create_block("blk2", "blk2")
        for blk in self.block1, self.block2:
            # blk.create_section("metadata", "md")  # create metatdata
            for i in range(2):
                blk.create_group("grp{}".format(i), "groups")
            for i in range(4):
                blk.create_data_array("da{}".format(i), "data_arrays",
                                      dtype="float",
                                      data=(1 + np.random.random((5))))
            for i in range(4):
                blk.create_tag("tag{}".format(i), "tags",
                               np.random.random((5,5)))
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


    def test_check_blocks(self):  # Done
        block = self.block1
        assert self.validator.errors['blocks'][0]['blk_err'] == []
        block._h5group.set_attr("name", None)
        assert self.validator.check_blocks(0)\
            ['blocks'][0]['blk_err'] == ['Name of some Block is missing']
        block._h5group.set_attr("type", None)
        self.validator.check_blocks(0)
        assert self.validator.errors['blocks'][0]['blk_err'] == ['Type of some Block is '
                                            'missing', 'Name of some Block is missing']

    def test_check_groups(self):  # Done
        group1 = self.block1.groups[0]
        group1._h5group.set_attr("name", None)
        self.validator.check_groups(0, 0)
        assert self.validator.errors['blocks'][0]['gro' \
                                'ups'][0]['grp_err'] == ['Name of some Group is missing']
        group2 = self.block2.groups[1]
        group2._h5group.set_attr("name", None)
        self.validator.check_groups(1,1)
        assert self.validator.errors['blocks'][1]['groups'][1]['grp_err'] == ['Name of some Group is missing']
        group2._h5group.set_attr("type", None)
        self.validator.check_groups(1, 1)
        assert self.validator.errors['blocks'][1]['groups'][1]['grp_err'] == [
            'Type of some Group is missing','Name of some Group is missing']

    def test_check_data_arrays(self):
        da1 = self.block1.data_arrays[0]
        da1.append_range_dimension([1, 2, 3, 4, 5, 6, 7, 8, 9])
        da1.append_set_dimension()
        da1.dimensions[1].labels = ["A", "B", "C", "D"]
        da1._h5group.set_attr("unit", "abcde")
        da1._h5group.set_attr("type", None)
        da1._h5group.set_attr("expansion_origin", 0.11) # poly not set
        self.validator.check_data_arrays(0,0)
        assert self.validator.errors['blocks'][0]['data_arrays'][0]['da_err'] == \
               ['Type of some DataArray is missing',
                'In some Range Dimensions, the number of '
                'ticks differ from the data entries', 'In some Set '
                'Dimensions, the number of labels differ from the data entries', 'Invalid units',
                'Expansion origins exist but polynomial coefficients are missing']

        da2 = self.block1.data_arrays[1]
        da2.append_set_dimension()
        da2.dimensions[0].labels = ["A", "B", "C", "D", "E"]
        da2.polynom_coefficients = [0.1, 0.2]
        self.validator.check_data_arrays(1, 0)
        assert self.validator.errors['blocks'][0]['data_arrays'][1]['da_err'] == \
               ["Polynomial coefficients exist but expansion origins are missing"]

        # Dimension mismatch missed out / change data_extent attr will also change shape

    def test_check_tags(self):
        tag1 = self.block1.tags[0]
        tag1.position = []
        self.validator.check_tag(0,0)
        assert self.validator.errors['blocks'][0]['tags'][0]['tag_err'] == ['Position is not set!']

        tag2 = self.block1.tags[1]
        tag2.units = ['abc']
        self.validator.check_tag(1,0)
        assert self.validator.errors['blocks'][0]['tags'][1]['tag_err'] == ['Invalid unit']

