# Copyright (c) 2013, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from nix import *

class TestBlock(unittest.TestCase):

    def setUp(self):
        self.file  = File.open("unittest.h5", FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")

    def tearDown(self):
        del self.file.blocks[0]
        self.file.close()

    def test_block_id(self):
        assert(self.block.id is not None)

    def test_block_name(self):
        def set_none():
            self.block.name = None

        assert(self.block.name is not None)
        self.assertRaises(Exception, set_none)

        self.block.name = "foo block"
        assert(self.block.name == "foo block")

    def test_block_type(self):
        def set_none():
            self.block.type = None

        assert(self.block.type is not None)
        self.assertRaises(Exception, set_none)

        self.block.type = "foo type"
        assert(self.block.type == "foo type")

    def test_block_definition(self):
        assert(self.block.definition is None)

        self.block.definition = "definition"
        assert(self.block.definition == "definition")

        self.block.definition = None
        assert(self.block.definition is None)

    def test_block_timestamps(self):
        created_at = self.block.created_at
        assert(created_at > 0)

        updated_at = self.block.updated_at
        assert(updated_at > 0)

        self.block.force_created_at(1403530068)
        assert(self.block.created_at == 1403530068)

    def test_block_data_arrays(self):
        assert(len(self.block.data_arrays) == 0)

        data_array = self.block.create_data_array("test data_array", "recordingsession")

        assert(len(self.block.data_arrays) == 1)

        # TODO implement __eq__ for DataArray
        #assert(data_array      in self.block.data_arrays)
        assert(data_array.id   in self.block.data_arrays)
        assert("notexist" not in self.block.data_arrays)

        assert(data_array.id == self.block.data_arrays[0].id)
        assert(data_array.id == self.block.data_arrays[-1].id)

        del self.block.data_arrays[0]

        assert(len(self.block.data_arrays) == 0)

    def test_block_data_tags(self):
        assert(len(self.block.data_tags) == 0)

        data_array = self.block.create_data_array("test array", "recording")
        data_tag = self.block.create_data_tag("test data_tag", "recordingsession", data_array)

        assert(len(self.block.data_tags) == 1)

        # TODO implement __eq__ for DataTag
        #assert(data_tag      in self.block.data_tags)
        assert(data_tag.id   in self.block.data_tags)
        assert("notexist" not in self.block.data_tags)

        assert(data_tag.id == self.block.data_tags[0].id)
        assert(data_tag.id == self.block.data_tags[-1].id)

        del self.block.data_tags[0]

        assert(len(self.block.data_tags) == 0)

    def test_block_simple_tags(self):
        assert(len(self.block.simple_tags) == 0)

        data_array = self.block.create_data_array("test array", "recording")
        simple_tag = self.block.create_simple_tag("test simple_tag", "recordingsession", [data_array])

        assert(len(self.block.simple_tags) == 1)

        # TODO implement __eq__ for SimpleTag
        #assert(simple_tag      in self.block.simple_tags)
        assert(simple_tag.id   in self.block.simple_tags)
        assert("notexist" not in self.block.simple_tags)

        assert(simple_tag.id == self.block.simple_tags[0].id)
        assert(simple_tag.id == self.block.simple_tags[-1].id)

        del self.block.simple_tags[0]

        assert(len(self.block.simple_tags) == 0)

    def test_block_sources(self):
        assert(len(self.block.sources) == 0)

        source = self.block.create_source("test source", "electrode")

        assert(len(self.block.sources) == 1)

        # TODO implement __eq__ for Source
        #assert(source      in self.block.sources)
        assert(source.id   in self.block.sources)
        assert("notexist" not in self.block.sources)

        assert(source.id == self.block.sources[0].id)
        assert(source.id == self.block.sources[-1].id)

        del self.block.sources[0]

        assert(len(self.block.sources) == 0)
