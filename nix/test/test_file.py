# Copyright (c) 2013, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from nix import *


class TestFile(unittest.TestCase):

    def setUp(self):
        self.file  = File.open("unittest.h5", FileMode.Overwrite)

    def tearDown(self):
        self.file.close()

    def test_file_format(self):
        assert(self.file.format == "nix")
        assert(self.file.version == "1.0")

    def test_file_timestamps(self):
        created_at = self.file.created_at
        assert(created_at > 0)

        updated_at = self.file.updated_at
        assert(updated_at > 0)

        self.file.force_created_at(1403530068)
        assert(self.file.created_at == 1403530068)

    def test_file_blocks(self):
        assert(len(self.file.blocks) == 0)

        block = self.file.create_block("test block", "recordingsession")

        assert(len(self.file.blocks) == 1)

        assert(block      in self.file.blocks)
        assert(block.id   in self.file.blocks)
        assert("notexist" not in self.file.blocks)

        assert(block.id == self.file.blocks[0].id)
        assert(block.id == self.file.blocks[-1].id)

        del self.file.blocks[0]

        assert(len(self.file.blocks) == 0)

    def test_file_sections(self):
        assert(len(self.file.sections) == 0)

        section = self.file.create_section("test section", "recordingsession")

        assert(len(self.file.sections) == 1)

        # TODO implement __eq__ for Section
        #assert(section      in self.file.sections)
        assert(section.id   in self.file.sections)
        assert("notexist" not in self.file.sections)

        assert(section.id == self.file.sections[0].id)
        assert(section.id == self.file.sections[-1].id)

        del self.file.sections[0]

        assert(len(self.file.sections) == 0)
