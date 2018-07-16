# -*- coding: utf-8 -*-
# Copyright © 2017, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
import nixio as nix
import unittest
from .tmp import TempDir


class TestContainer(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("containertest")
        self.testfilename = os.path.join(self.tmpdir.path, "containertest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "containertest")
        self.dataarray = self.block.create_data_array("test array",
                                                      "containertest",
                                                      data=[0])
        self.tag = self.block.create_tag("test tag", "containertest",
                                         position=[1.9, 20])
        self.positions = self.block.create_data_array("test pos",
                                                      "containertest",
                                                      data=[1])
        self.multi_tag = self.block.create_multi_tag("test multitag",
                                                     "containertest",
                                                     positions=self.positions)
        self.group = self.block.create_group("test group",
                                             "containertest")

        self.group.data_arrays.append(self.dataarray)
        self.group.tags.append(self.tag)
        self.group.multi_tags.append(self.multi_tag)

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_name_getter(self):
        self.assertEqual(self.block, self.file.blocks["test block"])
        self.assertEqual(self.dataarray, self.block.data_arrays["test array"])
        self.assertEqual(self.tag, self.block.tags["test tag"])
        self.assertEqual(self.multi_tag,
                         self.block.multi_tags["test multitag"])
        self.assertEqual(self.group, self.block.groups["test group"])
        self.assertEqual(self.positions, self.block.data_arrays["test pos"])

    def test_index_getter(self):
        self.assertEqual(self.block, self.file.blocks[0])
        self.assertEqual(self.dataarray, self.block.data_arrays[0])
        self.assertEqual(self.tag, self.block.tags[0])
        self.assertEqual(self.multi_tag,
                         self.block.multi_tags[0])
        self.assertEqual(self.group, self.block.groups[0])
        self.assertEqual(self.positions, self.block.data_arrays[1])

    def test_link_container_name_getter(self):
        self.assertEqual(self.dataarray, self.group.data_arrays["test array"])
        self.assertEqual(self.tag, self.group.tags["test tag"])
        self.assertEqual(self.multi_tag,
                         self.group.multi_tags["test multitag"])

    def test_link_container_index_getter(self):
        self.assertEqual(self.dataarray, self.group.data_arrays[0])
        self.assertEqual(self.tag, self.group.tags[0])
        self.assertEqual(self.multi_tag,
                         self.group.multi_tags[0])

    def test_parent_references(self):
        self.assertEqual(self.block._parent, self.file)
        self.assertEqual(self.group._parent, self.block)
        self.assertEqual(self.dataarray._parent, self.block)
        self.assertEqual(self.tag._parent, self.block)
        self.assertEqual(self.multi_tag._parent, self.block)
        self.assertEqual(self.positions._parent, self.block)

    def test_link_parent_references(self):
        self.assertEqual(self.group.data_arrays[0]._parent, self.block)
        self.assertEqual(self.group.tags[0]._parent, self.block)
        self.assertEqual(self.group.multi_tags[0]._parent, self.block)
