# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

import unittest
import numpy as np
from nixio import *


class _TestTag(unittest.TestCase):

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()

    def test_tag_eq(self):
        assert(self.my_tag == self.my_tag)
        assert(not self.my_tag == self.your_tag)
        assert(not self.my_tag is None)

    def test_tag_id(self):
        assert(self.my_tag.id is not None)

    def test_tag_name(self):
        assert(self.my_tag.name is not None)

    def test_tag_type(self):
        def set_none():
            self.my_tag.type = None

        assert(self.my_tag.type is not None)
        self.assertRaises(Exception, set_none)

        self.my_tag.type = "foo type"
        assert(self.my_tag.type == "foo type")

    def test_tag_definition(self):
        assert(self.my_tag.definition is None)

        self.my_tag.definition = "definition"
        assert(self.my_tag.definition == "definition")

        self.my_tag.definition = None
        assert(self.my_tag.definition is None)

    def test_tag_timestamps(self):
        created_at = self.my_tag.created_at
        assert(created_at > 0)

        updated_at = self.my_tag.updated_at
        assert(updated_at > 0)

        self.my_tag.force_created_at(1403530068)
        assert(self.my_tag.created_at == 1403530068)

    def test_tag_units(self):
        assert(self.my_tag.units == ())

        self.my_tag.units = ["mV", "ms"]
        assert(self.my_tag.units == ("mV", "ms"))

        self.my_tag.units = []
        assert(self.my_tag.units == ())

    def test_tag_position(self):
        assert(self.my_tag.position == (0, ))

        self.my_tag.position = (1.0, 2.0, 3.0)
        assert(self.my_tag.position == (1.0, 2.0, 3.0))

    def test_tag_extent(self):
        assert(self.my_tag.extent == ())

        self.my_tag.extent = (1.0, 2.0, 3.0)
        assert(self.my_tag.extent == (1.0, 2.0, 3.0))

        self.my_tag.extent = []
        assert(self.my_tag.extent == ())

    def test_tag_references(self):
        assert(len(self.my_tag.references) == 1)

        self.assertRaises(TypeError, lambda _: self.my_tag.references.append(100))

        reference1 = self.block.create_data_array("reference1", "stimuli", DataType.Int16, (1, ))
        reference2 = self.block.create_data_array("reference2", "stimuli", DataType.Int16, (1, ))

        self.my_tag.references.append(reference1)
        self.my_tag.references.append(reference2)

        assert(len(self.my_tag.references) == 3)
        assert(reference1 in self.my_tag.references)
        assert(reference2 in self.my_tag.references)

        del self.my_tag.references[reference2]
        assert(self.my_array in self.my_tag.references)
        assert(reference1 in self.my_tag.references)

        del self.my_tag.references[reference1]
        assert(len(self.my_tag.references) == 1)

    def test_tag_features(self):
        assert(len(self.my_tag.features) == 0)

        data_array = self.block.create_data_array("feature", "stimuli", DataType.Int16, (1, ))
        feature = self.my_tag.create_feature(data_array, LinkType.Untagged)

        assert(len(self.my_tag.features) == 1)

        assert(feature      in self.my_tag.features)
        assert(feature.id   in self.my_tag.features)
        assert("notexist" not in self.my_tag.features)

        assert(feature.id == self.my_tag.features[0].id)
        assert(feature.id == self.my_tag.features[-1].id)

        del self.my_tag.features[0]

        assert(len(self.my_tag.features) == 0)

    def test_tag_retrieve_feature_data(self):
        number_feat = self.block.create_data_array("number feature", "test", data=10.)
        ramp_data = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        ramp_feat = self.block.create_data_array("ramp feature", "test", data=np.asarray(ramp_data))
        ramp_feat.label = "voltage"
        ramp_feat.unit = "mV"
        dim = ramp_feat.append_sampled_dimension(1.0)
        dim.unit = "ms"

        pos_tag = self.block.create_tag("feature test", "test", [5.0])
        pos_tag.units = ["ms"]
        
        f1 = pos_tag.create_feature(number_feat, LinkType.Untagged)
        f2 = pos_tag.create_feature(ramp_feat, LinkType.Tagged)
        f3 = pos_tag.create_feature(ramp_feat, LinkType.Untagged)
        assert(len(pos_tag.features) == 3)

        data1 = pos_tag.retrieve_feature_data(0)
        data2 = pos_tag.retrieve_feature_data(1)
        data3 = pos_tag.retrieve_feature_data(2)
        
        assert(data1.size == 1) 
        assert(data2.size == 1) 
        assert(data3.size == len(ramp_data))
        
        # make the tag pointing to a slice
        pos_tag.extent = [2.0]
        data1 = pos_tag.retrieve_feature_data(0)
        data2 = pos_tag.retrieve_feature_data(1)
        data3 = pos_tag.retrieve_feature_data(2)
        
        assert(data1.size == 1) 
        assert(data2.size == 2) 
        assert(data3.size == len(ramp_data))


class TestTagCPP(_TestTag):

    def setUp(self):
        self.file     = File.open("unittest.h5", FileMode.Overwrite,
                                  backend="hdf5")
        self.block    = self.file.create_block("test block", "recordingsession")

        self.my_array = self.block.create_data_array("my array", "test", DataType.Int16, (1, ))
        self.my_tag   = self.block.create_tag(
            "my tag", "tag", [0]
        )
        self.my_tag.references.append(self.my_array)

        self.your_array = self.block.create_data_array("your array", "test", DataType.Int16, (1, ))
        self.your_tag = self.block.create_tag(
            "your tag", "tag", [0]
        )
        self.your_tag.references.append(self.your_array)


class TestTagPy(_TestTag):

    def setUp(self):
        self.file = File.open("unittest.h5", FileMode.Overwrite,
                              backend="h5py")

    def tearDown(self):
        pass

    def test_tag_eq(self):
        pass

    def test_tag_id(self):
        pass

    def test_tag_name(self):
        pass

    def test_tag_type(self):
        pass

    def test_tag_definition(self):
        pass

    def test_tag_timestamps(self):
        pass

    def test_tag_units(self):
        pass

    def test_tag_position(self):
        pass

    def test_tag_extent(self):
        pass

    def test_tag_references(self):
        pass

    def test_tag_features(self):
        pass

    def test_tag_retrieve_feature_data(self):
        pass
