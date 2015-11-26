# Copyright (c) 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

import unittest
from nix import *


class TestGroup(unittest.TestCase):

    def setUp(self):
        self.file  = File.open("unittest.h5", FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")

        self.my_array = self.block.create_data_array("my array", "test", DataType.Int16, (1, ))
        self.my_tag   = self.block.create_tag("my tag", "test", [0.25])
        self.my_group = self.block.create_group("my group", "group")
        self.my_group.data_arrays.append(self.my_array)
        self.my_group.tags.append(self.my_tag)

        self.your_array = self.block.create_data_array("your array", "test", DataType.Int16, (1, ))
        self.your_group = self.block.create_group("your group", "group")
        self.your_group.data_arrays.append(self.your_array)


    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()

    def test_group_eq(self):
        assert(self.my_group == self.my_group)
        assert(not self.my_group == self.your_group)
        assert(self.my_group is not None)

    def test_group_id(self):
        assert(self.my_group.id is not None)

    def test_group_name(self):
        assert(self.my_group.name is not None)

    def test_group_type(self):
        def set_none():
            self.my_group.type = None

        assert(self.my_group.type is not None)
        self.assertRaises(Exception, set_none)

        self.my_group.type = "foo type"
        assert(self.my_group.type == "foo type")

    def test_group_definition(self):
        assert(self.my_group.definition is None)

        self.my_group.definition = "definition"
        assert(self.my_group.definition == "definition")

        self.my_group.definition = None
        assert(self.my_group.definition is None)

    def test_group_timestamps(self):
        created_at = self.my_group.created_at
        assert(created_at > 0)

        updated_at = self.my_group.updated_at
        assert(updated_at > 0)

        self.my_group.force_created_at(1403530068)
        assert(self.my_group.created_at == 1403530068)

    def test_group_data_arrays(self):
        assert(len(self.my_group.data_arrays) == 1)

        self.assertRaises(TypeError, lambda _: self.my_group.data_arrays.append(100))

        a1 = self.block.create_data_array("reference1", "stimuli", DataType.Int16, (1, ))
        a2 = self.block.create_data_array("reference2", "stimuli", DataType.Int16, (1, ))

        self.my_group.data_arrays.append(a1)
        self.my_group.data_arrays.append(a2)

        assert(len(self.my_group.data_arrays) == 3)
        assert(a1 in self.my_group.data_arrays)
        assert(a2 in self.my_group.data_arrays)

        del self.my_group.data_arrays[a2]
        assert(self.my_array in self.my_group.data_arrays)
        assert(a1 in self.my_group.data_arrays)

        del self.my_group.data_arrays[a1]
        assert(len(self.my_group.data_arrays) == 1)

    def test_group_tags(self):
        assert(len(self.my_group.tags) == 1)

        self.assertRaises(TypeError, lambda _: self.my_group.tags.append(100))

        t1 = self.block.create_tag("tag1", "stimuli", [1.0])
        t2 = self.block.create_tag("tag2", "stimuli", [2.])

        self.my_group.tags.append(t1)
        self.my_group.tags.append(t2)

        assert(len(self.my_group.tags) == 3)
        assert(t1 in self.my_group.tags)
        assert(t2 in self.my_group.tags)

        del self.my_group.tags[t2]
        assert(self.my_tag in self.my_group.tags)
        assert(t1 in self.my_group.tags)

        del self.my_group.tags[t1]
        assert(len(self.my_group.tags) == 1)

        self.my_group.tags.extend([t1, t2])
        assert(len(self.my_group.tags) == 3)
