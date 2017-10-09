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

class _TestMultiTag(unittest.TestCase):
    testfilename = "mtagtest.h5"

    def setUp(self):
        iv = 1.0
        ticks = [1.2, 2.3, 3.4, 4.5, 6.7]
        unit = "ms"

        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")

        self.my_array = self.block.create_data_array("my array", "test",
                                                     nix.DataType.Int16,
                                                     (0, 0))
        self.my_tag = self.block.create_multi_tag(
            "my tag", "tag", self.my_array
        )

        self.your_array = self.block.create_data_array("your array", "test",
                                                       nix.DataType.Int16,
                                                       (0, 0))
        self.your_tag = self.block.create_multi_tag(
            "your tag", "tag", self.your_array
        )

        self.data_array = self.block.create_data_array("featureTest", "test",
                                                       nix.DataType.Double,
                                                       (2, 10, 5))

        data = np.zeros((2, 10, 5))
        value = 0.
        for i in range(2):
            value = 0
            for j in range(10):
                for k in range(5):
                    value += 1
                    data[i, j, k] = value

        self.data_array[:, :, :] = data

        set_dim = self.data_array.append_set_dimension()
        set_dim.labels = ["label_a", "label_b"]
        sampled_dim = self.data_array.append_sampled_dimension(iv)
        sampled_dim.unit = unit
        range_dim = self.data_array.append_range_dimension(ticks)
        range_dim.unit = unit

        event_positions = np.zeros((2, 3))
        event_positions[0, 0] = 0.0
        event_positions[0, 1] = 3.0
        event_positions[0, 2] = 3.4

        event_positions[1, 0] = 0.0
        event_positions[1, 1] = 8.0
        event_positions[1, 2] = 2.3

        event_extents = np.zeros((2, 3))
        event_extents[0, 0] = 0.0
        event_extents[0, 1] = 6.0
        event_extents[0, 2] = 2.3

        event_extents[1, 0] = 0.0
        event_extents[1, 1] = 3.0
        event_extents[1, 2] = 2.0

        event_labels = ["event 1", "event 2"]
        dim_labels = ["dim 0", "dim 1", "dim 2"]

        self.event_array = self.block.create_data_array("positions", "test",
                                                        data=event_positions)

        self.extent_array = self.block.create_data_array("extents", "test",
                                                         data=event_extents)
        extent_set_dim = self.extent_array.append_set_dimension()
        extent_set_dim.labels = event_labels
        extent_set_dim = self.extent_array.append_set_dimension()
        extent_set_dim.labels = dim_labels

        self.feature_tag = self.block.create_multi_tag("feature_tag", "events",
                                                       self.event_array)
        self.feature_tag.extents = self.extent_array
        self.feature_tag.references.append(self.data_array)

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        os.remove(self.testfilename)

    def test_multi_tag_eq(self):
        assert(self.my_tag == self.my_tag)
        assert(not self.my_tag == self.your_tag)
        assert(self.my_tag is not None)

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

        new_positions = self.block.create_data_array("pos", "position",
                                                     nix.DataType.Int16,
                                                     (0, 0))
        self.my_tag.positions = new_positions
        assert(self.my_tag.positions == new_positions)

        self.assertRaises(TypeError, set_none)

        self.my_tag.positions = old_positions
        assert(self.my_tag.positions == old_positions)

    def test_multi_tag_extents(self):
        assert(self.my_tag.extents is None)

        new_extents = self.block.create_data_array("ext", "extent",
                                                   nix.DataType.Int16, (0, 0))
        self.my_tag.extents = new_extents
        assert(self.my_tag.extents == new_extents)

        self.my_tag.extents = None
        assert(self.my_tag.extents is None)

    def test_multi_tag_references(self):
        assert(len(self.my_tag.references) == 0)

        self.assertRaises(TypeError,
                          lambda _: self.my_tag.references.append(100))

        reference1 = self.block.create_data_array("reference1", "stimuli",
                                                  nix.DataType.Int16, (0, ))
        reference2 = self.block.create_data_array("reference2", "stimuli",
                                                  nix.DataType.Int16, (0, ))

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

        data_array = self.block.create_data_array("feature", "stimuli",
                                                  nix.DataType.Int16, (0, ))
        feature = self.my_tag.create_feature(data_array,
                                             nix.LinkType.Untagged)
        assert(len(self.my_tag.features) == 1)

        assert(feature in self.my_tag.features)
        assert(feature.id in self.my_tag.features)
        assert("notexist" not in self.my_tag.features)

        assert(feature.id == self.my_tag.features[0].id)
        assert(feature.id == self.my_tag.features[-1].id)

        del self.my_tag.features[0]

        assert(len(self.my_tag.features) == 0)

    def test_multi_tag_retrieve_data(self):
        sample_iv = 0.001
        x = np.arange(0, 10, sample_iv)
        y = np.sin(2*np.pi*x)

        block = self.block
        da = block.create_data_array("sin", "data", data=y)
        da.unit = 'dB'
        dim = da.append_sampled_dimension(sample_iv)
        dim.unit = 's'

        pos = block.create_data_array('pos1', 'positions',
                                      data=np.array([0.]).reshape((1, 1)))
        pos.append_set_dimension()
        pos.append_set_dimension()
        pos.unit = 'ms'
        ext = block.create_data_array('ext1', 'extents',
                                      data=np.array([2000.]).reshape((1, 1)))
        ext.append_set_dimension()
        ext.append_set_dimension()
        ext.unit = 'ms'

        mtag = block.create_multi_tag("sin1", "tag", pos)
        mtag.extents = ext
        mtag.units = ['ms']
        mtag.references.append(da)

        assert(mtag.retrieve_data(0, 0).shape == (2000,))
        assert(np.array_equal(y[:2000], mtag.retrieve_data(0, 0)[:]))

        # get by name
        data = mtag.retrieve_data(0, da.name)
        assert(data.shape == (2000,))
        assert(np.array_equal(y[:2000], data[:]))

        # multi dimensional data
        sample_iv = 1.0
        ticks = [1.2, 2.3, 3.4, 4.5, 6.7]
        unit = "ms"
        pos = self.block.create_data_array("pos", "test",
                                           data=[[1, 1, 1],
                                                 [1, 1, 1]])
        pos.append_set_dimension()
        pos.append_set_dimension()
        ext = self.block.create_data_array("ext", "test",
                                           data=[[2, 5, 2],
                                                 [0, 4, 1]])
        ext.append_set_dimension()
        ext.append_set_dimension()
        units = ["none", "ms", "ms"]
        data = np.random.random((3, 10, 5))
        da = self.block.create_data_array("dimtest", "test",
                                          data=data)
        setdim = da.append_set_dimension()
        setdim.labels = ["Label A", "Label B", "Label D"]
        samdim = da.append_sampled_dimension(sample_iv)
        samdim.unit = unit
        randim = da.append_range_dimension(ticks)
        randim.unit = unit

        postag = self.block.create_multi_tag("postag", "event", pos)
        postag.references.append(da)
        postag.units = units

        segtag = self.block.create_multi_tag("region", "segment", pos)
        segtag.references.append(da)
        segtag.extents = ext
        segtag.units = units

        posdata = postag.retrieve_data(0, 0)
        assert(len(posdata.shape) == 3)
        assert(posdata.shape == (1, 1, 1))
        assert(np.isclose(posdata[0, 0, 0], data[1, 1, 0]))

        posdata = postag.retrieve_data(1, 0)
        assert(len(posdata.shape) == 3)
        assert(posdata.shape == (1, 1, 1))
        assert(np.isclose(posdata[0, 0, 0], data[1, 1, 0]))

        segdata = segtag.retrieve_data(0, 0)
        assert(len(segdata.shape) == 3)
        assert(segdata.shape == (2, 5, 2))

        segdata = segtag.retrieve_data(1, 0)
        assert(len(segdata.shape) == 3)
        assert(segdata.shape == (1, 4, 1))

    def test_multi_tag_feature_data(self):
        index_data = self.block.create_data_array("indexed feature data",
                                                  "test",
                                                  dtype=nix.DataType.Double,
                                                  shape=(10, 10))
        dim1 = index_data.append_sampled_dimension(1.0)
        dim1.unit = "ms"
        dim2 = index_data.append_sampled_dimension(1.0)
        dim2.unit = "ms"

        data1 = np.zeros((10, 10))
        value = 0.0
        total = 0.0
        for i in range(10):
            value = 100 * i
            for j in range(10):
                value += 1
                data1[i, j] = value
                total += data1[i, j]

        index_data[:, :] = data1

        tagged_data = self.block.create_data_array("tagged feature data",
                                                   "test",
                                                   dtype=nix.DataType.Double,
                                                   shape=(10, 20, 10))
        dim1 = tagged_data.append_sampled_dimension(1.0)
        dim1.unit = "ms"
        dim2 = tagged_data.append_sampled_dimension(1.0)
        dim2.unit = "ms"
        dim3 = tagged_data.append_sampled_dimension(1.0)
        dim3.unit = "ms"

        data2 = np.zeros((10, 20, 10))
        for i in range(10):
            value = 100 * i
            for j in range(20):
                for k in range(10):
                    value += 1
                    data2[i, j, k] = value

        tagged_data[:, :, :] = data2

        self.feature_tag.create_feature(index_data, nix.LinkType.Indexed)
        self.feature_tag.create_feature(tagged_data, nix.LinkType.Tagged)
        self.feature_tag.create_feature(index_data, nix.LinkType.Untagged)

        # preparations done, actually test
        # print(self.feature_tag.features)
        assert(len(self.feature_tag.features) == 3)

        # indexed feature
        feat_data = self.feature_tag.retrieve_feature_data(0, 0)
        assert(len(feat_data.shape) == 2)
        assert(feat_data.size == 10)
        assert(np.sum(feat_data) == 55)

        data_view = self.feature_tag.retrieve_feature_data(9, 0)
        assert(np.sum(data_view[:, :]) == 9055)

        # untagged feature
        data_view = self.feature_tag.retrieve_feature_data(0, 2)
        assert(data_view.size == 100)

        data_view = self.feature_tag.retrieve_feature_data(0, 2)
        assert(data_view.size == 100)
        assert(np.sum(data_view) == total)

        # tagged feature
        data_view = self.feature_tag.retrieve_feature_data(0, 1)
        assert(len(data_view.shape) == 3)

        data_view = self.feature_tag.retrieve_feature_data(1, 1)
        assert(len(data_view.shape) == 3)

        # === retrieve by name ===
        # indexed feature
        feat_data = self.feature_tag.retrieve_feature_data(0, index_data.name)
        assert(len(feat_data.shape) == 2)
        assert(feat_data.size == 10)
        assert(np.sum(feat_data) == 55)

        data_view = self.feature_tag.retrieve_feature_data(9, index_data.name)
        assert(np.sum(data_view[:, :]) == 9055)

        # tagged feature
        data_view = self.feature_tag.retrieve_feature_data(0, tagged_data.name)
        assert(len(data_view.shape) == 3)

        data_view = self.feature_tag.retrieve_feature_data(1, tagged_data.name)
        assert(len(data_view.shape) == 3)

        def out_of_bounds():
            self.feature_tag.retrieve_feature_data(2, 1)

        self.assertRaises(IndexError,  out_of_bounds)
