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
        self.prop    = self.section.create_property("test property", Value(0))
        self.prop_s  = self.section.create_property("test str", DataType.String)
        self.other   = self.section.create_property("other property", DataType.Int64)

    def tearDown(self):
        del self.file.sections[self.section.id]
        self.file.close()

    def test_property_eq(self):
        assert(self.prop == self.prop)
        assert(not self.prop == self.other)
        assert(not self.prop == None)

    def test_property_id(self):
        assert(self.prop.id is not None)

    def test_property_name(self):
        def set_none():
            self.prop.name = None

        assert(self.prop.name is not None)
        self.assertRaises(Exception, set_none)

        self.prop.name = "foo section"
        assert(self.prop.name == "foo section")

    def test_property_definition(self):
        assert(self.prop.definition is None)

        self.prop.definition = "definition"
        assert(self.prop.definition == "definition")

        self.prop.definition = None
        assert(self.prop.definition is None)

    def test_property_mapping(self):
        assert(self.prop.mapping is None)

        self.prop.mapping = "mapping"
        assert(self.prop.mapping == "mapping")

        self.prop.mapping = None
        assert(self.prop.mapping is None)

    def test_property_values(self):
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

        self.prop_s.values = [Value("foo"), Value("bar")]
        assert(self.prop_s.data_type == DataType.String)
        assert(len(self.prop_s.values) == 2)

        assert(self.prop_s.values[0] == Value("foo"))
        assert(Value("foo") in self.prop_s.values)
        assert(self.prop_s.values[0] == "foo")
        assert("foo" in self.prop_s.values)
        assert(self.prop_s.values[0] != Value("bla"))
        assert(Value("bla") not in self.prop_s.values)
        assert(self.prop_s.values[0] != "bla")
        assert("bla" not in self.prop_s.values)


class TestValue(unittest.TestCase):

    def test_value_int(self):
        value = Value(10)
        other = Value(11)

        assert(value.data_type == DataType.Int64)

        assert(value == value)
        assert(value == 10)

        assert(value != other)
        assert(value != 11)

        value.value = 20
        assert(value == Value(20))
        assert(value == 20)
        assert(value.value == 20)

    def test_value_float(self):
        value = Value(47.11)
        other = Value(3.14)

        assert(value.data_type == DataType.Double)

        assert(value == value)
        assert(value == 47.11)

        assert(value != other)
        assert(value != 3.14)

        value.value = 66.6
        assert(value == Value(66.6))
        assert(value == 66.6)
        assert(value.value == 66.6)


    def test_value_bool(self):
        value = Value(True)
        other = Value(False)

        assert(value.data_type == DataType.Bool)

        assert(value == value)
        assert(value == True)

        assert(value != other)
        assert(value != False)

        value.value = False
        assert(value == other)

    def test_value_str(self):
        value = Value("foo")
        other = Value("bar")

        assert(value.data_type == DataType.String)

        assert(value == value)
        assert(value == "foo")

        assert(value != other)
        assert(value != "bar")

        value.value = "wrtlbrmpft"
        assert(value == Value("wrtlbrmpft"))
        assert(value == "wrtlbrmpft")
        assert(value.value == "wrtlbrmpft")

    def test_value_attrs(self):
        value = Value(0)

        value.reference = "a"
        assert(value.reference == "a")

        value.filename = "b"
        assert(value.filename == "b")

        value.filename = "c"
        assert(value.filename == "c")

        value.checksum = "d"
        assert(value.checksum == "d")

        value.uncertainty = 0.5
        assert(value.uncertainty == 0.5)
