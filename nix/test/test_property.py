# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from nix import *

class TestProperty(unittest.TestCase):

    def setUp(self):
        self.file    = File.open("unittest.h5", FileMode.Overwrite)
        self.section = self.file.create_section("test section", "recordingsession")
        self.prop    = self.section.create_property("test property")
        self.other   = self.section.create_property("other property")

    def tearDown(self):
        del self.file.sections[self.section.id]
        self.file.close()

    def test_section_eq(self):
        assert(self.prop == self.prop)
        assert(not self.prop == self.other)
        assert(not self.prop == None)

    def test_section_id(self):
        assert(self.prop.id is not None)

    def test_section_name(self):
        def set_none():
            self.prop.name = None

        assert(self.prop.name is not None)
        self.assertRaises(Exception, set_none)

        self.prop.name = "foo section"
        assert(self.prop.name == "foo section")

    def test_section_definition(self):
        assert(self.prop.definition is None)

        self.prop.definition = "definition"
        assert(self.prop.definition == "definition")

        self.prop.definition = None
        assert(self.prop.definition is None)

    def test_section_mapping(self):
        assert(self.prop.mapping is None)

        self.prop.mapping = "mapping"
        assert(self.prop.mapping == "mapping")

        self.prop.mapping = None
        assert(self.prop.mapping is None)

    def test_section_values(self):
        self.prop.values = [Value(10)]
        assert(self.prop.data_type == DataType.Int64)
        assert(len(self.prop.values) == 1)

        assert(self.prop.values[0] == Value(10))
        assert(Value(10) in self.prop.values)
        assert(self.prop.values[0] == 10)
        assert(10 in self.prop.values)
        assert(self.prop.values[0] != Value(1337))
        assert(Value(1337) not in self.prop.values)
        assert(self.prop.values[0] != 42)
        assert(42 not in self.prop.values)

        self.prop.delete_values()
        assert(len(self.prop.values) == 0)

        self.prop.values = [Value("foo"), Value("bar")]
        assert(self.prop.data_type == DataType.String)
        assert(len(self.prop.values) == 2)

        assert(self.prop.values[0] == Value("foo"))
        assert(Value("foo") in self.prop.values)
        assert(self.prop.values[0] == "foo")
        assert("foo" in self.prop.values)
        assert(self.prop.values[0] != Value("bla"))
        assert(Value("bla") not in self.prop.values)
        assert(self.prop.values[0] != "bla")
        assert("bla" not in self.prop.values)
