# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from nix import *


class TestMultiTag(unittest.TestCase):

    def setUp(self):
        self.file     = File.open("unittest.h5", FileMode.Overwrite)
        self.block    = self.file.create_block("test block", "recordingsession")

        self.my_array = self.block.create_data_array("my array", "test", DataType.Int16, (0, 0))
        self.my_tag   = self.block.create_multi_tag(
            "my tag", "tag", self.my_array
        )

        self.your_array = self.block.create_data_array("your array", "test", DataType.Int16, (0, 0))
        self.your_tag = self.block.create_multi_tag(
            "your tag", "tag", self.your_array
        )

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()

    def test_multi_tag_eq(self):
        assert(self.my_tag == self.my_tag)
        assert(not self.my_tag == self.your_tag)
        assert(not self.my_tag is None)

    def test_multi_tag_id(self):
        assert(self.my_tag.id is not None)

    def test_multi_tag_name(self):
        assert(self.my_tag.name is not None)

    def test_multi_tag_type(self):
        def set_none():
            self.my_tag.type = None

        assert(self.my_tag.type is not None)
        self.assertRaises(Exception, set_none)

        self.my_tag.type = "foo type"
        assert(self.my_tag.type == "foo type")

    def test_multi_tag_definition(self):
        assert(self.my_tag.definition is None)

        self.my_tag.definition = "definition"
        assert(self.my_tag.definition == "definition")

        self.my_tag.definition = None
        assert(self.my_tag.definition is None)

    def test_multi_tag_timestamps(self):
        created_at = self.my_tag.created_at
        assert(created_at > 0)

        updated_at = self.my_tag.updated_at
        assert(updated_at > 0)

        self.my_tag.force_created_at(1403530068)
        assert(self.my_tag.created_at == 1403530068)

    def test_multi_tag_units(self):
        assert(self.my_tag.units == ())

        self.my_tag.units = ["mV", "ms"]
        assert(self.my_tag.units == ("mV", "ms"))

        self.my_tag.units = []  # () also works!
        assert(self.my_tag.units == ())

    def test_multi_tag_positions(self):
        def set_none():
            self.my_tag.positions = None

        assert(self.my_tag.positions is not None)
        old_positions = self.my_tag.positions

        new_positions = self.block.create_data_array("pos", "position", DataType.Int16, (0, 0))
        self.my_tag.positions = new_positions
        assert(self.my_tag.positions == new_positions)

        self.assertRaises(TypeError, set_none)

        self.my_tag.positions = old_positions
        assert(self.my_tag.positions == old_positions)

    def test_multi_tag_extents(self):
        assert(self.my_tag.extents is None)

        new_extents = self.block.create_data_array("ext", "extent", DataType.Int16, (0, 0))
        self.my_tag.extents = new_extents
        assert(self.my_tag.extents == new_extents)

        self.my_tag.extents = None
        assert(self.my_tag.extents is None)

    def test_multi_tag_references(self):
        assert(len(self.my_tag.references) == 0)

        self.assertRaises(TypeError, lambda _: self.my_tag.references.append(100))

        reference1 = self.block.create_data_array("reference1", "stimuli", DataType.Int16, (0, ))
        reference2 = self.block.create_data_array("reference2", "stimuli", DataType.Int16, (0, ))

        self.my_tag.references.append(reference1)
        self.my_tag.references.append(reference2)

        assert(len(self.my_tag.references) == 2)
        assert(reference1 in self.my_tag.references)
        assert(reference2 in self.my_tag.references)

        del self.my_tag.references[reference2]
        assert(self.my_tag.references[0] == reference1)

        del self.my_tag.references[reference1]
        assert(len(self.my_tag.references) == 0)

    def test_multi_tag_features(self):
        assert(len(self.my_tag.features) == 0)

        data_array = self.block.create_data_array("feature", "stimuli", DataType.Int16, (0, ))
        feature = self.my_tag.create_feature(data_array, LinkType.Untagged)
        assert(len(self.my_tag.features) == 1)

        assert(feature      in self.my_tag.features)
        assert(feature.id   in self.my_tag.features)
        assert("notexist" not in self.my_tag.features)

        assert(feature.id == self.my_tag.features[0].id)
        assert(feature.id == self.my_tag.features[-1].id)

        del self.my_tag.features[0]

        assert(len(self.my_tag.features) == 0)

    def test_multi_tag_retrieve_data(self):
        import numpy as np

        sample_iv = 0.001
        x = np.arange(0, 10, sample_iv)
        y = np.sin(2*np.pi*x)

        block = self.block
        da = block.create_data_array("sin", "data", data=y)
        da.unit = 'dB'
        dim = da.append_sampled_dimension(sample_iv)
        dim.unit = 's'

        pos = block.create_data_array('pos1', 'positions', data=np.array([0.]).reshape((1, 1)))
        pos.append_set_dimension()
        pos.append_set_dimension()
        pos.unit = 'ms'
        ext = block.create_data_array('ext1', 'extents', data=np.array([2000.]).reshape((1, 1)))
        ext.append_set_dimension()
        ext.append_set_dimension()
        ext.unit = 'ms'

        tag = block.create_multi_tag("sin1", "tag", pos)
        tag.extents = ext
        tag.units = ['ms']
        tag.references.append(da)

        assert(tag.retrieve_data(0, 0).shape == (2001,))
        assert(np.array_equal(y[:2001], tag.retrieve_data(0, 0)[:]))
