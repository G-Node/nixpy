# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)
import os

import unittest
import numpy as np
import nixio as nix


skip_cpp = not hasattr(nix, "core")


class TagTestBase(unittest.TestCase):

    backend = None
    testfilename = "tagtest.h5"

    def setUp(self):
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite,
                                  backend=self.backend)
        self.block = self.file.create_block("test block", "recordingsession")

        self.my_array = self.block.create_data_array("my array", "test",
                                                     nix.DataType.Int16, (1, ))
        self.my_tag = self.block.create_tag(
            "my tag", "tag", [0]
        )
        self.my_tag.references.append(self.my_array)

        self.your_array = self.block.create_data_array(
            "your array", "test", nix.DataType.Int16, (1, )
        )
        self.your_tag = self.block.create_tag(
            "your tag", "tag", [0]
        )
        self.your_tag.references.append(self.your_array)

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        os.remove(self.testfilename)

    def test_tag_eq(self):
        assert(self.my_tag == self.my_tag)
        assert(not self.my_tag == self.your_tag)
        assert(self.my_tag is not None)

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

        self.assertRaises(TypeError,
                          lambda _: self.my_tag.references.append(100))

        reference1 = self.block.create_data_array("reference1", "stimuli",
                                                  nix.DataType.Int16, (1, ))
        reference2 = self.block.create_data_array("reference2", "stimuli",
                                                  nix.DataType.Int16, (1, ))

        self.my_tag.references.append(reference1)
        self.my_tag.references.append(reference2)

        assert(reference1.name in self.my_tag.references)

        assert(len(self.my_tag.references) == 3)
        assert(reference1 in self.my_tag.references)
        assert(reference2 in self.my_tag.references)

        # id and name access
        assert(reference1 == self.my_tag.references[reference1.name])
        assert(reference1 == self.my_tag.references[reference1.id])
        assert(reference2 == self.my_tag.references[reference2.name])
        assert(reference2 == self.my_tag.references[reference2.id])

        assert(reference1.name in self.my_tag.references)
        assert(reference2.name in self.my_tag.references)
        assert(reference1.id in self.my_tag.references)
        assert(reference2.id in self.my_tag.references)

        del self.my_tag.references[reference2]
        assert(self.my_array in self.my_tag.references)
        assert(reference1 in self.my_tag.references)

        del self.my_tag.references[reference1]
        assert(len(self.my_tag.references) == 1)

    def test_tag_features(self):
        assert(len(self.my_tag.features) == 0)

        data_array = self.block.create_data_array("feature", "stimuli",
                                                  nix.DataType.Int16, (1, ))
        feature = self.my_tag.create_feature(data_array, nix.LinkType.Untagged)

        assert(len(self.my_tag.features) == 1)

        assert(feature in self.my_tag.features)
        assert(feature.id in self.my_tag.features)
        assert("notexist" not in self.my_tag.features)

        assert(feature.id == self.my_tag.features[0].id)
        assert(feature.id == self.my_tag.features[-1].id)

        # id and name access
        assert(feature.id == self.my_tag.features[feature.id].id)
        assert(feature.id == self.my_tag.features[data_array.id].id)
        assert(feature.id == self.my_tag.features[data_array.name].id)
        assert(data_array == self.my_tag.features[data_array.id].data)
        assert(data_array == self.my_tag.features[data_array.name].data)

        assert(data_array.id in self.my_tag.features)
        assert(data_array.name in self.my_tag.features)

        del self.my_tag.features[0]

        assert(len(self.my_tag.features) == 0)

    def test_tag_retrieve_data(self):
        sample_iv = 1.0
        ticks = [1.2, 2.3, 3.4, 4.5, 6.7]
        unit = "ms"
        pos = [0.0, 2.0, 3.4]
        ext = [0.0, 6.0, 2.3]
        units = ["none", "ms", "ms"]
        data = np.random.random((2, 10, 5))
        da = self.block.create_data_array("dimtest", "test",
                                          data=data)
        setdim = da.append_set_dimension()
        setdim.labels = ["Label A", "Label B"]
        samdim = da.append_sampled_dimension(sample_iv)
        samdim.unit = unit
        randim = da.append_range_dimension(ticks)
        randim.unit = unit

        postag = self.block.create_tag("postag", "event", pos)
        postag.references.append(da)
        postag.units = units

        segtag = self.block.create_tag("region", "segment", pos)
        segtag.references.append(da)
        segtag.extent = ext
        segtag.units = units

        posdata = postag.retrieve_data(0)
        assert(len(posdata.shape) == 3)
        assert(posdata.shape == (1, 1, 1))

        segdata = segtag.retrieve_data(0)
        assert(len(segdata.shape) == 3)
        assert(segdata.shape == (1, 7, 2))

        # retrieve data by id and name
        posdata = postag.retrieve_data(da.name)
        assert(len(posdata.shape) == 3)
        assert(posdata.shape == (1, 1, 1))
        segdata = segtag.retrieve_data(da.name)
        assert(len(segdata.shape) == 3)
        assert(segdata.shape == (1, 7, 2))

        posdata = postag.retrieve_data(da.id)
        assert(len(posdata.shape) == 3)
        assert(posdata.shape == (1, 1, 1))
        segdata = segtag.retrieve_data(da.id)
        assert(len(segdata.shape) == 3)
        assert(segdata.shape == (1, 7, 2))

    def test_tag_retrieve_feature_data(self):
        number_feat = self.block.create_data_array("number feature", "test",
                                                   data=10.)
        ramp_data = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        ramp_feat = self.block.create_data_array("ramp feature", "test",
                                                 data=np.asarray(ramp_data))
        ramp_feat.label = "voltage"
        ramp_feat.unit = "mV"
        dim = ramp_feat.append_sampled_dimension(1.0)
        dim.unit = "ms"

        pos_tag = self.block.create_tag("feature test", "test", [5.0])
        pos_tag.units = ["ms"]

        pos_tag.create_feature(number_feat, nix.LinkType.Untagged)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Tagged)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Untagged)
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
        assert(data2.size == 3)
        assert(data3.size == len(ramp_data))

        # get by name
        data1 = pos_tag.retrieve_feature_data(number_feat.name)
        data2 = pos_tag.retrieve_feature_data(ramp_feat.name)

        assert(data1.size == 1)
        assert(data2.size == 3)


@unittest.skipIf(skip_cpp, "HDF5 backend not available.")
class TestTagCPP(TagTestBase):

    backend = "hdf5"


class TestTagPy(TagTestBase):

    backend = "h5py"
