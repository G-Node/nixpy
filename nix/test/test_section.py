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
        self.other   = self.file.create_section("other section", "recordingsession")

    def tearDown(self):
        del self.file.sections[self.section.id]
        del self.file.sections[self.other.id]
        self.file.close()

    def test_section_eq(self):
        assert(self.section == self.section)
        assert(not self.section == self.other)
        assert(not self.section == None)

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

    def test_section_find_sections(self):
        for i in range(2): self.section.create_section("level1-p0-s" + str(i), "dummy")
        for i in range(2): self.section.sections[0].create_section("level2-p1-s" + str(i), "dummy")
        for i in range(2): self.section.sections[1].create_section("level2-p2-s" + str(i), "dummy")
        for i in range(2): self.section.sections[0].sections[0].create_section("level3-p1-s" + str(i), "dummy")

        assert(len(self.section.find_sections()) == 9)
        assert(len(self.section.find_sections(limit=1)) == 3)
        assert(len(self.section.find_sections(filtr=lambda x : "level2-p1-s" in x.name)) == 2)
        assert(len(self.section.find_sections(filtr=lambda x : "level2-p1-s" in x.name, limit=1)) == 0)

        assert(len(self.section.find_related()) == 3)
        assert(len(self.section.sections[0].find_related()) == 5)


    def test_section_properties(self):
        assert(len(self.section.properties) == 0)

        prop = self.section.create_property("test prop")

        assert(len(self.section.properties) == 1)

        assert(self.section.has_property_with_name("test prop"))
        assert(not self.section.has_property_with_name("notexist"))
        assert(self.section.get_property_with_name("test prop") is not None)
        assert(self.section.get_property_with_name("notexist") is None)

        # TODO better test when proxy is implemented
        assert(len(self.section._inherited_properties()) == 1)

        # TODO implement __eq__ for property
        #assert(prop      in self.section.properties)
        assert(prop.id   in self.section.properties)
        assert("notexist" not in self.section.properties)

        assert(prop.id == self.section.properties[0].id)
        assert(prop.id == self.section.properties[-1].id)

        del self.section.properties[0]

        assert(len(self.section.properties) == 0)
