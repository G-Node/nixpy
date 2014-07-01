# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from nix import *

class TestDataArray(unittest.TestCase):

    def setUp(self):
        self.file  = File.open("unittest.h5", FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.array = self.block.create_data_array("test array", "signal")
        self.other = self.block.create_data_array("other array", "signal")

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()

    def test_data_array_eq(self):
        assert(self.array == self.array)
        assert(not self.array == self.other)
        assert(not self.array == None)

    def test_data_array_id(self):
        assert(self.array.id is not None)

    def test_data_array_name(self):
        def set_none():
            self.array.name = None

        assert(self.array.name is not None)
        self.assertRaises(Exception, set_none)

        self.array.name = "foo array"
        assert(self.array.name == "foo array")

    def test_data_array_type(self):
        def set_none():
            self.array.type = None

        assert(self.array.type is not None)
        self.assertRaises(Exception, set_none)

        self.array.type = "foo type"
        assert(self.array.type == "foo type")

    def test_data_array_definition(self):
        assert(self.array.definition is None)

        self.array.definition = "definition"
        assert(self.array.definition == "definition")

        self.array.definition = None
        assert(self.array.definition is None)

    def test_data_array_timestamps(self):
        created_at = self.array.created_at
        assert(created_at > 0)

        updated_at = self.array.updated_at
        assert(updated_at > 0)

        self.array.force_created_at(1403530068)
        assert(self.array.created_at == 1403530068)

    def test_data_array_label(self):
        assert(self.array.label is None)

        self.array.label = "label"
        assert(self.array.label == "label")

        self.array.label = None
        assert(self.array.label is None)

    def test_data_array_unit(self):
        assert(self.array.unit is None)

        self.array.unit = "mV"
        assert(self.array.unit == "mV")

        self.array.unit = None
        assert(self.array.unit is None)

    def test_data_array_exp_origin(self):
        assert(self.array.expansion_origin is None)

        self.array.expansion_origin = 10.2
        assert(self.array.expansion_origin == 10.2)

        self.array.expansion_origin = None
        assert(self.array.expansion_origin is None)

    def test_data_array_coefficients(self):
        assert(self.array.polynom_coefficients == [])

        self.array.polynom_coefficients = [1.1, 2.2]
        assert(self.array.polynom_coefficients == [1.1, 2.2])

        # TODO delete does not work

    def test_data_array_data(self):
        assert(self.array.polynom_coefficients == [])
        assert(not self.array.has_data())

        data = [float(i) for i in range(100)]
        self.array.data = data
        assert(self.array.has_data())
        assert(self.array.data == data)

        # TODO delete does not work
