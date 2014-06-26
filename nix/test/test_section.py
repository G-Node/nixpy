# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from nix import *

class TestSection(unittest.TestCase):

    def setUp(self):
        self.file    = File.open("unittest.h5", FileMode.Overwrite)
        self.section = self.file.create_section("test section", "recordingsession")

    def tearDown(self):
        del self.file.sections[0]
        self.file.close()

    def test_section_id(self):
        assert(self.section.id is not None)

    def test_section_name(self):
        def set_none():
            self.section.name = None

        assert(self.section.name is not None)
        self.assertRaises(Exception, set_none)

        self.section.name = "foo section"
        assert(self.section.name == "foo section")

    def test_section_type(self):
        def set_none():
            self.section.type = None

        assert(self.section.type is not None)
        self.assertRaises(Exception, set_none)

        self.section.type = "foo type"
        assert(self.section.type == "foo type")

    def test_section_definition(self):
        assert(self.section.definition is None)

        self.section.definition = "definition"
        assert(self.section.definition == "definition")

        self.section.definition = None
        assert(self.section.definition is None)

    def test_section_mapping(self):
        assert(self.section.mapping is None)

        self.section.mapping = "mapping"
        assert(self.section.mapping == "mapping")

        self.section.mapping = None
        assert(self.section.mapping is None)

    def test_section_repository(self):
        assert(self.section.repository is None)

        self.section.repository = "repository"
        assert(self.section.repository == "repository")

        self.section.repository = None
        assert(self.section.repository is None)

    def test_section_sections(self):
        assert(len(self.section.sections) == 0)

        child = self.section.create_section("test section", "electrode")
        assert(child.parent == self.section)

        assert(len(self.section.sections) == 1)

        assert(child      in self.section.sections)
        assert(child.id   in self.section.sections)
        assert("notexist" not in self.section.sections)

        assert(child.id == self.section.sections[0].id)
        assert(child.id == self.section.sections[-1].id)

        del self.section.sections[0]

        assert(len(self.section.sections) == 0)

    def test_section_properties(self):
        assert(len(self.section.properties) == 0)

        prop = self.section.create_property("test prop", "notype")

        assert(len(self.section.properties) == 1)

        # TODO implement __eq__ for property
        #assert(prop      in self.section.properties)
        assert(prop.id   in self.section.properties)
        assert("notexist" not in self.section.properties)

        assert(prop.id == self.section.properties[0].id)
        assert(prop.id == self.section.properties[-1].id)

        del self.section.properties[0]

        assert(len(self.section.properties) == 0)
