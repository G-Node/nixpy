# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from nix import *

class TestSource(unittest.TestCase):

    def setUp(self):
        self.file   = File.open("unittest.h5", FileMode.Overwrite)
        self.block  = self.file.create_block("test block", "recordingsession")
        self.source = self.block.create_source("test source", "recordingchannel")
        self.other  = self.block.create_source("other source", "sometype")

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()

    def test_source_eq(self):
        assert(self.source == self.source)
        assert(not self.source == self.other)
        assert(not self.source == None)

    def test_source_id(self):
        assert(self.source.id is not None)

    def test_source_name(self):
        assert(self.source.name is not None)

    def test_source_type(self):
        def set_none():
            self.source.type = None

        assert(self.source.type is not None)
        self.assertRaises(Exception, set_none)

        self.source.type = "foo type"
        assert(self.source.type == "foo type")

    def test_source_definition(self):
        assert(self.source.definition is None)

        self.source.definition = "definition"
        assert(self.source.definition == "definition")

        self.source.definition = None
        assert(self.source.definition is None)

    def test_source_timestamps(self):
        created_at = self.source.created_at
        assert(created_at > 0)

        updated_at = self.source.updated_at
        assert(updated_at > 0)

        self.source.force_created_at(1403530068)
        assert(self.source.created_at == 1403530068)

    def test_source_sources(self):
        assert(len(self.source.sources) == 0)

        source = self.source.create_source("test source", "electrode")

        assert(len(self.source.sources) == 1)

        assert(source      in self.source.sources)
        assert(source.id   in self.source.sources)
        assert("notexist" not in self.source.sources)

        assert(source.id == self.source.sources[0].id)
        assert(source.id == self.source.sources[-1].id)

        del self.source.sources[0]

        assert(len(self.source.sources) == 0)

    def test_source_find_sources(self):
        for i in range(2): self.source.create_source("level1-p0-s" + str(i), "dummy")
        for i in range(2): self.source.sources[0].create_source("level2-p1-s" + str(i), "dummy")
        for i in range(2): self.source.sources[1].create_source("level2-p2-s" + str(i), "dummy")
        for i in range(2): self.source.sources[0].sources[0].create_source("level3-p1-s" + str(i), "dummy")

        assert(len(self.source.find_sources()) == 9)
        assert(len(self.source.find_sources(limit=1)) == 3)
        assert(len(self.source.find_sources(filtr=lambda x : "level2-p1-s" in x.name)) == 2)
        assert(len(self.source.find_sources(filtr=lambda x : "level2-p1-s" in x.name, limit=1)) == 0)
