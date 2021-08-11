# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from nixio.exceptions.exceptions import InvalidSlice
import os
import time
import unittest
from collections import OrderedDict
import numpy as np
import nixio as nix
from nixio.exceptions import DuplicateName, UnsupportedLinkType
from .tmp import TempDir


class TestMultiTags(unittest.TestCase):

    def setUp(self):
        interval = 1.0
        ticks = [1.2, 2.3, 3.4, 4.5, 6.7]
        unit = "ms"

        self.tmpdir = TempDir("mtagtest")
        self.testfilename = os.path.join(self.tmpdir.path, "mtagtest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")

        self.my_array = self.block.create_data_array("my array", "test", nix.DataType.Int16, (0, 0))
        self.my_tag = self.block.create_multi_tag("my tag", "tag", self.my_array)

        self.your_array = self.block.create_data_array("your array", "test", nix.DataType.Int16, (0, 0))
        self.your_tag = self.block.create_multi_tag("your tag", "tag", self.your_array)

        self.data_array = self.block.create_data_array("featureTest", "test", nix.DataType.Double, (2, 10, 5))

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
        sampled_dim = self.data_array.append_sampled_dimension(interval)
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
        event_extents[0, 0] = 1.0
        event_extents[0, 1] = 6.0
        event_extents[0, 2] = 2.3

        event_extents[1, 0] = 1.0
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
        self.tmpdir.cleanup()

    def test_multi_tag_new_constructor(self):
        pos = np.random.random_sample((2, 3))
        ext = np.random.random_sample((2, 3))
        mt = self.block.create_multi_tag("conv_test", "test", pos, ext)
        np.testing.assert_almost_equal(pos, mt.positions[:])
        np.testing.assert_almost_equal(ext, mt.extents[:])
        # try reset positions and ext
        assert mt.positions.name == "conv_test-positions"
        assert mt.positions.type == "test-positions"
        assert mt.extents.name == "conv_test-extents"
        assert mt.extents.type == "test-extents"
        # test positions extents deleted if multitag creation failed
        pos = None
        ext = np.random.random_sample((2, 3))
        self.assertRaises(ValueError, self.block.create_multi_tag,
                          "err_test", "test", pos, ext)
        self.block.create_data_array("dup_test-"
                                     "positions", "test", data=[0])
        pos = np.random.random_sample((2, 3))
        ext = np.random.random_sample((2, 3))
        self.assertRaises(DuplicateName, self.block.create_multi_tag,
                          "dup_test", "test", pos, ext)
        del self.block.data_arrays["dup_test-positions"]
        self.block.create_data_array("dup_test2-"
                                     "extents", "test", data=[0])
        pos = np.random.random_sample((2, 3))
        ext = np.random.random_sample((2, 3))
        self.assertRaises(DuplicateName, self.block.create_multi_tag,
                          "dup_test2", "test", pos, ext)
        pos = np.random.random_sample((2, 3))
        ext = [None, None]
        self.assertRaises(TypeError, self.block.create_multi_tag,
                          "dup_test3", "test", pos, ext)

    def test_multi_tag_flex(self):
        pos1d = self.block.create_data_array("pos1", "pos", data=[[0], [1]])
        pos1d1d = self.block.create_data_array("pos1d1d", "pos", data=[0, 1])
        pos2d = self.block.create_data_array("pos2", "pos", data=[[0, 0], [1, 1]])
        pos3d = self.block.create_data_array("pos3", "pos", data=[[0, 1, 2], [1, 2, 3]])
        ext1d = self.block.create_data_array('ext1', 'ext', data=[[1], [1]])
        ext1d1d = self.block.create_data_array('ext1d1d', 'ext', data=[1, 1])
        ext2d = self.block.create_data_array('ext2', 'ext', data=[[1, 2], [0, 2]])
        ext3d = self.block.create_data_array('ext3', 'ext', data=[[1, 1, 1], [1, 1, 1]])
        mt1d = self.block.create_multi_tag("mt1d", "mt", pos1d)
        mt1d.extents = ext1d
        mt1d1d = self.block.create_multi_tag("mt1d1d", "mt", pos1d1d)
        mt1d1d.extents = ext1d1d
        mt2d = self.block.create_multi_tag("mt2d", "mt", pos2d)
        mt2d.extents = ext2d
        mt3d = self.block.create_multi_tag("mt3d", "mt", pos3d)
        mt3d.extents = ext3d
        # create some references
        da1d = self.block.create_data_array('ref1d', 'ref', data=np.arange(10))
        da1d.append_sampled_dimension(1., label="time", unit="s")
        da2d = self.block.create_data_array('ref2d', 'ref', data=np.arange(100).reshape((10, 10)))
        da2d.append_sampled_dimension(1., label="time", unit="s")
        da2d.append_set_dimension()
        da3d = self.block.create_data_array('ref3d', 'ref', data=np.arange(1000).reshape((10, 10, 10)))
        da3d.append_sampled_dimension(1., label="time", unit="s")
        da3d.append_set_dimension()
        da3d.append_set_dimension()
        mt1d.references.extend([da1d, da2d, da3d])
        mt1d1d.references.extend([da1d, da2d, da3d])
        mt2d.references.extend([da1d, da2d, da3d])
        mt3d.references.extend([da1d, da2d, da3d])
        np.testing.assert_almost_equal(mt1d.tagged_data(0, 0)[:], da1d[0:1])
        np.testing.assert_almost_equal(mt1d.tagged_data(0, 1)[:], da2d[0:1, :])
        np.testing.assert_almost_equal(mt1d.tagged_data(0, 2)[:], da3d[0:1, :, :])
        np.testing.assert_almost_equal(mt1d1d.tagged_data(0, 0)[:], da1d[0:1])
        np.testing.assert_almost_equal(mt1d1d.tagged_data(0, 1)[:], da2d[0:1, :])
        np.testing.assert_almost_equal(mt1d1d.tagged_data(0, 2)[:], da3d[0:1, :, :])
        np.testing.assert_almost_equal(mt2d.tagged_data(0, 0)[:], da1d[0:1])
        np.testing.assert_almost_equal(mt2d.tagged_data(0, 1)[:], da2d[0:1, 0:2])
        np.testing.assert_almost_equal(mt2d.tagged_data(0, 2)[:], da3d[0:1, 0:2, :])
        np.testing.assert_almost_equal(mt3d.tagged_data(1, 0)[:], da1d[1:2])
        np.testing.assert_almost_equal(mt3d.tagged_data(1, 1)[:], da2d[1:2, 2:3])
        np.testing.assert_almost_equal(mt3d.tagged_data(1, 2)[:], da3d[1:2, 2:3, 3:4])

    def test_multi_tag_eq(self):
        assert self.my_tag == self.my_tag
        assert not self.my_tag == self.your_tag
        assert self.my_tag is not None

    def test_multi_tag_id(self):
        assert self.my_tag.id is not None

    def test_multi_tag_name(self):
        assert self.my_tag.name is not None

    def test_multi_tag_type(self):
        def set_none():
            self.my_tag.type = None

        assert self.my_tag.type is not None
        self.assertRaises(Exception, set_none)

        self.my_tag.type = "foo type"
        assert self.my_tag.type == "foo type"

    def test_multi_tag_definition(self):
        assert self.my_tag.definition is None

        self.my_tag.definition = "definition"
        assert self.my_tag.definition == "definition"

        self.my_tag.definition = None
        assert self.my_tag.definition is None

    def test_multi_tag_timestamps(self):
        created_at = self.my_tag.created_at
        assert created_at > 0

        updated_at = self.my_tag.updated_at
        assert updated_at > 0

        self.my_tag.force_created_at(1403530068)
        assert self.my_tag.created_at == 1403530068

    def test_multi_tag_units(self):
        assert self.my_tag.units == ()

        self.my_tag.units = ["mV", "ms"]
        assert self.my_tag.units == ("mV", "ms")

        self.my_tag.units = []  # () also works!
        assert self.my_tag.units == ()

    def test_multi_tag_positions(self):
        def set_none():
            self.my_tag.positions = None

        assert self.my_tag.positions is not None
        old_positions = self.my_tag.positions

        new_positions = self.block.create_data_array("pos", "position",
                                                     nix.DataType.Int16,
                                                     (0, 0))
        self.my_tag.positions = new_positions
        assert self.my_tag.positions == new_positions

        self.assertRaises(TypeError, set_none)

        self.my_tag.positions = old_positions
        assert self.my_tag.positions == old_positions

    def test_multi_tag_extents(self):
        assert self.my_tag.extents is None

        new_extents = self.block.create_data_array("ext", "extent",
                                                   nix.DataType.Int16, (0, 0))
        self.my_tag.extents = new_extents
        assert self.my_tag.extents == new_extents

        self.my_tag.extents = None
        assert self.my_tag.extents is None

    def test_multi_tag_references(self):
        assert len(self.my_tag.references) == 0

        self.assertRaises(TypeError, self.my_tag.references.append, 100)

        reference1 = self.block.create_data_array("reference1", "stimuli",
                                                  nix.DataType.Int16, (0,))
        reference2 = self.block.create_data_array("reference2", "stimuli",
                                                  nix.DataType.Int16, (0,))

        self.my_tag.references.append(reference1)
        self.my_tag.references.append(reference2)

        assert len(self.my_tag.references) == 2
        assert reference1 in self.my_tag.references
        assert reference2 in self.my_tag.references

        # id and name access
        assert reference1 == self.my_tag.references[reference1.name]
        assert reference1 == self.my_tag.references[reference1.id]
        assert reference2 == self.my_tag.references[reference2.name]
        assert reference2 == self.my_tag.references[reference2.id]

        assert reference1.name in self.my_tag.references
        assert reference2.name in self.my_tag.references
        assert reference1.id in self.my_tag.references
        assert reference2.id in self.my_tag.references

        del self.my_tag.references[reference2]
        assert self.my_tag.references[0] == reference1

        del self.my_tag.references[reference1]
        assert len(self.my_tag.references) == 0

    def test_multi_tag_features(self):
        assert len(self.my_tag.features) == 0

        data_array = self.block.create_data_array("feature", "stimuli",
                                                  nix.DataType.Int16, (0,))
        feature = self.my_tag.create_feature(data_array,
                                             nix.LinkType.Untagged)
        assert len(self.my_tag.features) == 1

        assert feature in self.my_tag.features
        assert feature.id in self.my_tag.features
        assert "notexist" not in self.my_tag.features

        assert feature.id == self.my_tag.features[0].id
        assert feature.id == self.my_tag.features[-1].id

        # id and name access
        assert feature.id == self.my_tag.features[feature.id].id
        assert feature.id == self.my_tag.features[data_array.id].id
        assert feature.id == self.my_tag.features[data_array.name].id
        assert data_array == self.my_tag.features[data_array.id].data
        assert data_array == self.my_tag.features[data_array.name].data

        assert data_array.id in self.my_tag.features
        assert data_array.name in self.my_tag.features

        data_frame = self.block.create_data_frame(
            "dataframe feature", "test",
            col_dict=OrderedDict([("number", nix.DataType.Float)]),
            data=[(10.,)]
        )
        df_feature = self.my_tag.create_feature(data_frame, nix.LinkType.Untagged)

        assert len(self.my_tag.features) == 2

        assert df_feature in self.my_tag.features
        assert df_feature.id in self.my_tag.features

        assert df_feature.id == self.my_tag.features[1].id
        assert df_feature.id == self.my_tag.features[-1].id

        # id and name access
        assert df_feature.id == self.my_tag.features[df_feature.id].id
        assert df_feature.id == self.my_tag.features[data_frame.id].id
        assert df_feature.id == self.my_tag.features[data_frame.name].id
        assert data_frame == self.my_tag.features[data_frame.id].data
        assert data_frame == self.my_tag.features[data_frame.name].data

        assert data_frame.id in self.my_tag.features
        assert data_frame.name in self.my_tag.features

        assert isinstance(self.my_tag.features[0].data, nix.DataArray)
        assert isinstance(self.my_tag.features[1].data, nix.DataFrame)

        del self.my_tag.features[0]
        assert len(self.my_tag.features) == 1
        del self.my_tag.features[0]
        assert len(self.my_tag.features) == 0

    def test_multi_tag_tagged_data(self):
        sample_iv = 0.001
        x_data = np.arange(0, 10, sample_iv)
        y_data = np.sin(2 * np.pi * x_data)

        block = self.block
        da = block.create_data_array("sin", "data", data=y_data)
        da.unit = 'dB'
        dim = da.append_sampled_dimension(sample_iv)
        dim.unit = 's'

        pos = block.create_data_array('pos1', 'positions', data=np.array([0.]).reshape(1, 1))
        pos.append_set_dimension()
        pos.append_set_dimension()
        pos.unit = 'ms'
        ext = block.create_data_array('ext1', 'extents', data=np.array([2000.]).reshape(1, 1))
        ext.append_set_dimension()
        ext.append_set_dimension()
        ext.unit = 'ms'

        mtag = block.create_multi_tag("sin1", "tag", pos)
        mtag.extents = ext
        mtag.units = ['ms']
        mtag.references.append(da)

        assert mtag.tagged_data(0, 0).shape == (2000,)
        assert np.array_equal(y_data[:2000], mtag.tagged_data(0, 0)[:])
        assert mtag.tagged_data(0, 0, stop_rule=nix.SliceMode.Inclusive).shape == (2001,)
        assert np.array_equal(y_data[:2001], mtag.tagged_data(0, 0, stop_rule=nix.SliceMode.Inclusive)[:])

        # get by name
        data = mtag.tagged_data(0, da.name)
        assert data.shape == (2000,)
        assert np.array_equal(y_data[:2000], data[:])

        # get by id
        data = mtag.tagged_data(0, da.id)
        assert data.shape == (2000,)
        assert np.array_equal(y_data[:2000], data[:])

        # multi dimensional data
        # position 1 should fail since the position in the third dimension does not point to a valid point
        # positon 2 and 3 should deliver valid DataViews
        # same for segment 0 should again return an invalid DataView because of dimension 3
        sample_iv = 1.0
        ticks = [1.2, 2.3, 3.4, 4.5, 6.7]
        unit = "ms"
        pos = self.block.create_data_array("pos", "test", data=[[1, 1, 1], [1, 1, 1.2], [1, 1, 1.2]])
        pos.append_set_dimension()
        pos.append_set_dimension()
        ext = self.block.create_data_array("ext", "test", data=[[1, 5, 2], [1, 5, 2], [0, 4, 1]])
        ext.append_set_dimension()
        ext.append_set_dimension()
        units = ["none", "ms", "ms"]
        data = np.random.random_sample((3, 10, 5))
        da = self.block.create_data_array("dimtest", "test", data=data)
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

        posdata = postag.tagged_data(0, 0)
        assert not posdata.valid
        assert "InvalidSlice error" in posdata.debug_message
        assert posdata.data_extent is None
        assert posdata.shape is None
        with self.assertRaises(InvalidSlice):
            posdata._write_data(np.random.randn(1))
        assert sum(posdata[:].shape) == 0

        posdata = postag.tagged_data(1, 0)
        assert posdata.valid
        assert posdata.debug_message == ""
        assert len(posdata.shape) == 3
        assert posdata.shape == (1, 1, 1)
        assert np.isclose(posdata[0, 0, 0], data[1, 1, 0])

        posdata = postag.tagged_data(2, 0)
        assert len(posdata.shape) == 3
        assert posdata.shape == (1, 1, 1)
        assert np.isclose(posdata[0, 0, 0], data[1, 1, 0])

        segdata = segtag.tagged_data(1, 0)
        assert len(segdata.shape) == 3
        assert segdata.shape == (1, 5, 2)

        segdata = segtag.tagged_data(2, 0)
        assert len(segdata.shape) == 3
        assert segdata.shape == (1, 4, 1)

        # retrieve all positions for all references
        for ridx, _ in enumerate(mtag.references):
            for pidx, _ in enumerate(mtag.positions):
                mtag.tagged_data(pidx, ridx)

        wrong_pos = self.block.create_data_array("incorpos", "test", data=[[1, 1, 1], [100, 1, 1]])
        wrong_pos.append_set_dimension()
        wrong_pos.append_set_dimension()
        postag.positions = wrong_pos
        self.assertRaises(IndexError, postag.tagged_data, 1, 1)
        wrong_ext = self.block.create_data_array("incorext", "test", data=[[1, 500, 2], [0, 4, 1]])
        wrong_ext.append_set_dimension()
        wrong_ext.append_set_dimension()
        segtag.extents = wrong_ext
        self.assertRaises(IndexError, segtag.tagged_data, 0, 1)

    def test_multi_tag_data_coefficients(self):
        sample_iv = 0.001
        x_data = np.arange(0, 10, sample_iv)
        y_data = np.sin(2 * np.pi * x_data)

        block = self.block
        da = block.create_data_array("sin", "data", data=y_data)
        da.unit = 'V'
        da.polynom_coefficients = (10, 0.3)
        dim = da.append_sampled_dimension(sample_iv)
        dim.unit = 's'

        pos = block.create_data_array('pos1', 'positions', data=np.array([0.]).reshape(1, 1))
        pos.append_set_dimension()
        pos.append_set_dimension()
        pos.unit = 'ms'
        ext = block.create_data_array('ext1', 'extents', data=np.array([2000.]).reshape(1, 1))
        ext.append_set_dimension()
        ext.append_set_dimension()
        ext.unit = 'ms'

        mtag = block.create_multi_tag("sin1", "tag", pos)
        mtag.extents = ext
        mtag.units = ['ms']
        mtag.references.append(da)

        assert np.array_equal(da[:2000], mtag.tagged_data(0, 0)[:])

        da.expansion_origin = 0.89
        assert np.array_equal(da[:2000], mtag.tagged_data(0, 0)[:])

    def test_multi_tag_tagged_data_1d(self):
        # MultiTags to vectors behave a bit differently
        # Testing separately
        oneddata = self.block.create_data_array("1dda", "data",
                                                data=list(range(100)))
        oneddata.append_sampled_dimension(0.1)
        onedpos = self.block.create_data_array("1dpos", "positions",
                                               data=[1, 9, 9.5])
        onedmtag = self.block.create_multi_tag("2dmt", "mtag",
                                               positions=onedpos)
        onedmtag.references.append(oneddata)
        for pidx, _ in enumerate(onedmtag.positions):
            onedmtag.tagged_data(pidx, 0)

    def test_multi_tag_feature_data(self):
        index_data = self.block.create_data_array("indexed feature data", "test",
                                                  dtype=nix.DataType.Double, shape=(10, 10))
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

        tagged_data = self.block.create_data_array("tagged feature data", "test",
                                                   dtype=nix.DataType.Double, shape=(10, 20, 10))
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
        assert len(self.feature_tag.features) == 3

        # indexed feature
        feat_data = self.feature_tag.feature_data(0, 0)
        assert len(feat_data.shape) == 2
        assert feat_data.size == 10
        assert np.sum(feat_data) == 55

        # disabled, don't understand how it could ever have worked,
        # there are only 3 positions
        data_view = self.feature_tag.feature_data(9, 0)
        assert np.sum(data_view[:, :]) == 9055

        # untagged feature
        data_view = self.feature_tag.feature_data(0, 2)
        assert data_view.size == 100

        data_view = self.feature_tag.feature_data(0, 2)
        assert data_view.size == 100
        assert np.sum(data_view) == total

        # tagged feature
        data_view = self.feature_tag.feature_data(0, 1)
        assert len(data_view.shape) == 3

        data_view = self.feature_tag.feature_data(1, 1)
        assert len(data_view.shape) == 3

        # === retrieve by name ===
        # indexed feature
        feat_data = self.feature_tag.feature_data(0, index_data.name)
        assert len(feat_data.shape) == 2
        assert feat_data.size == 10
        assert np.sum(feat_data) == 55

        # disabled, there are only 3 positions
        data_view = self.feature_tag.feature_data(9, index_data.name)
        assert np.sum(data_view[:, :]) == 9055

        # tagged feature
        data_view = self.feature_tag.feature_data(0, tagged_data.name)
        assert len(data_view.shape) == 3

        data_view = self.feature_tag.feature_data(1, tagged_data.name)
        assert len(data_view.shape) == 3

        def out_of_bounds():
            self.feature_tag.feature_data(2, 1)

        self.assertRaises(IndexError, out_of_bounds)

    def test_timestamp_autoupdate(self):
        pos = self.block.create_data_array("positions.time", "test.time",
                                           nix.DataType.Int16, (0, 0))
        mtag = self.block.create_multi_tag("mtag.time", "test.time", pos)

        mtagtime = mtag.updated_at
        time.sleep(1)  # wait for time to change
        mtag.positions = self.block.create_data_array("pos2.time",
                                                      "test.time",
                                                      nix.DataType.Int8, (0,))
        self.assertNotEqual(mtag.updated_at, mtagtime)

        mtagtime = mtag.updated_at
        time.sleep(1)  # wait for time to change
        mtag.extents = self.block.create_data_array("extents.time",
                                                    "test.time",
                                                    nix.DataType.Int8, (0,))
        self.assertNotEqual(mtag.updated_at, mtagtime)

    def test_timestamp_noautoupdate(self):
        self.file.auto_update_timestamps = False
        pos = self.block.create_data_array("positions.time", "test.time",
                                           nix.DataType.Int16, (0, 0))
        mtag = self.block.create_multi_tag("mtag.time", "test.time", pos)

        mtagtime = mtag.updated_at
        time.sleep(1)  # wait for time to change
        mtag.positions = self.block.create_data_array("pos2.time",
                                                      "test.time",
                                                      nix.DataType.Int8, (0,))
        self.assertEqual(mtag.updated_at, mtagtime)

        mtagtime = mtag.updated_at
        time.sleep(1)  # wait for time to change
        mtag.extents = self.block.create_data_array("extents.time",
                                                    "test.time",
                                                    nix.DataType.Int8, (0,))
        self.assertEqual(mtag.updated_at, mtagtime)

    def test_multi_tag_feature_dataframe(self):
        numberdata = np.random.random(20)
        number_feat = self.block.create_data_frame(
            "number feature", "test",
            col_dict=OrderedDict([("number", nix.DataType.Float)]),
            data=[(n,) for n in numberdata]
        )
        column_descriptions = OrderedDict([("name", nix.DataType.String),
                                           ("duration", nix.DataType.Double)])
        values = [("One", 0.1), ("Two", 0.2), ("Three", 0.3), ("Four", 0.4),
                  ("Five", 0.5), ("Six", 0.6), ("Seven", 0.7), ("Eight", 0.8),
                  ("Nine", 0.9), ("Ten", 1.0)]
        ramp_feat = self.block.create_data_frame("ramp feature", "test",
                                                 col_dict=column_descriptions,
                                                 data=values)
        ramp_feat.label = "voltage"
        ramp_feat.units = (None, "s")

        pos_tag = self.block.create_multi_tag("feature test", "test", [4, 7, 8])

        with self.assertRaises(UnsupportedLinkType):
            pos_tag.create_feature(number_feat, nix.LinkType.Tagged)
        pos_tag.create_feature(number_feat, nix.LinkType.Untagged)
        pos_tag.create_feature(number_feat, nix.LinkType.Indexed)
        with self.assertRaises(UnsupportedLinkType):
            pos_tag.create_feature(ramp_feat, nix.LinkType.Tagged)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Untagged)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Indexed)
        assert len(pos_tag.features) == 4

        for idx, _ in enumerate(pos_tag.positions):
            data1 = pos_tag.feature_data(idx, 0)
            data2 = pos_tag.feature_data(idx, 1)
            data3 = pos_tag.feature_data(idx, 2)
            data4 = pos_tag.feature_data(idx, 3)

            # check expected data
            assert np.all(data1[:] == number_feat[:])
            assert np.all(data2[:] == number_feat[idx])
            assert np.all(data3[:] == ramp_feat[:])
            assert np.all(data4[:] == ramp_feat[idx])

        # add extents (should have no effect)
        extents = self.block.create_data_array("feature test.extents", "test",
                                               data=[2, 2, 5])
        pos_tag.extents = extents
        for idx, _ in enumerate(pos_tag.positions):
            data1 = pos_tag.feature_data(idx, 0)
            data2 = pos_tag.feature_data(idx, 1)
            data3 = pos_tag.feature_data(idx, 2)
            data4 = pos_tag.feature_data(idx, 3)

            # check expected data
            assert np.all(data1[:] == number_feat[:])
            assert np.all(data2[:] == number_feat[idx])
            assert np.all(data3[:] == ramp_feat[:])
            assert np.all(data4[:] == ramp_feat[idx])

    def test_multi_tag_tagged_data_slice_mode(self):
        data = np.random.random_sample((3, 100, 10))
        da = self.block.create_data_array("signals", "test.signals", data=data)
        da.unit = "mV"
        da.append_set_dimension(labels=["A", "B", "C"])
        sample_iv = 0.001
        timedim = da.append_sampled_dimension(sampling_interval=sample_iv)
        timedim.unit = "s"
        posdim = da.append_range_dimension([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9])
        posdim.unit = "mm"

        # exact_tag has a pos+ext that is exactly equal to a dimension tick
        exact_tag = self.block.create_multi_tag("tickpoint", "test.tag",
                                                positions=[(0, 0.03, 0.0011), (1, 0.05, 0.0015)],
                                                extents=[(1, 0.02, 0.0005), (1, 0.04, 0.0003)])
        exact_tag.units = ["none", "s", "m"]

        exact_tag.references.append(da)

        # FIRST TAG
        # dim2: [0.001, 0.002, ..., 0.03, 0.031, ..., 0.049, 0.05, 0.051, ...]
        #                           ^ pos [30]               ^ pos+ext [50]
        # Inclusive mode includes index 50, exclusive does not
        #
        # dim3: [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
        #             ^ pos [1]                ^ pos+ext [6]
        # Inclusive mode includes index 6, exclusive does not

        slice_default = exact_tag.tagged_data(0, 0)
        assert slice_default.shape == (1, 20, 5)
        np.testing.assert_array_equal(slice_default, da[0:1, 30:50, 1:6])  # default exclusive

        slice_inclusive = exact_tag.tagged_data(0, 0, stop_rule=nix.SliceMode.Inclusive)
        assert slice_inclusive.shape == (2, 21, 6)
        np.testing.assert_array_equal(slice_inclusive, da[0:2, 30:51, 1:7])

        slice_exclusive = exact_tag.tagged_data(0, 0, stop_rule=nix.SliceMode.Exclusive)
        assert slice_exclusive.shape == (1, 20, 5)
        np.testing.assert_array_equal(slice_exclusive, da[0:1, 30:50, 1:6])

        # SECOND TAG
        # dim2: [0.001, 0.002, ..., 0.05, 0.051, ..., 0.089, 0.09, 0.091, ...]
        #                           ^ pos [50]               ^ pos+ext [90]
        # Inclusive mode includes index 90, exclusive does not
        #
        # dim3: [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
        #                                 ^ pos [5]        ^ pos+ext [8]
        # Inclusive mode includes index 8, exclusive does not

        slice_default = exact_tag.tagged_data(1, 0)
        assert slice_default.shape == (1, 40, 3)
        np.testing.assert_array_equal(slice_default, da[1:2, 50:90, 5:8])  # default exclusive

        slice_inclusive = exact_tag.tagged_data(1, 0, stop_rule=nix.SliceMode.Inclusive)
        assert slice_inclusive.shape == (2, 41, 4)
        np.testing.assert_array_equal(slice_inclusive, da[1:3, 50:91, 5:9])

        slice_exclusive = exact_tag.tagged_data(1, 0, stop_rule=nix.SliceMode.Exclusive)
        assert slice_exclusive.shape == (1, 40, 3)
        np.testing.assert_array_equal(slice_exclusive, da[1:2, 50:90, 5:8])

        # midpoint_tag has a pos+ext that falls between dimension ticks
        midpoint_tag = self.block.create_multi_tag("midpoint", "test.tag",
                                                   positions=([0, 0.03, 0.0011], [1, 0.05, 0.0015]),
                                                   extents=([1, 0.0301, 0.00051], [1, 0.0401, 0.00031]))  # .1 offset
        midpoint_tag.units = ["none", "s", "m"]

        # FIRST TAG
        # dim2: [0.001, 0.002, ..., 0.03, 0.031, ..., 0.059, 0.06,|   0.061, ...]
        #                           ^ pos [30]                    ^ pos+ext [60] + 0.1
        # Both inclusive and exclusive include index 60
        #
        # dim3: [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6,|   1.7, 1.8, 1.9]
        #             ^ pos [1]                    ^ pos+ext [6] + 0.1
        # Both inclusive and exclusive include index 6

        midpoint_tag.references.append(da)

        # all slicing is inclusive since the pos+ext points are between ticks
        slice_default = midpoint_tag.tagged_data(0, 0)
        assert slice_default.shape == (1, 31, 6)
        np.testing.assert_array_equal(slice_default, da[0:1, 30:61, 1:7])

        slice_inclusive = midpoint_tag.tagged_data(0, 0, stop_rule=nix.SliceMode.Inclusive)
        assert slice_inclusive.shape == (2, 31, 6)
        np.testing.assert_array_equal(slice_inclusive, da[0:2, 30:61, 1:7])

        slice_exclusive = midpoint_tag.tagged_data(0, 0, stop_rule=nix.SliceMode.Exclusive)
        assert slice_exclusive.shape == (1, 31, 6)
        np.testing.assert_array_equal(slice_exclusive, da[0:1, 30:61, 1:7])

        # SECOND TAG
        # dim2: [0.001, 0.002, ..., 0.05, 0.051, ..., 0.089, 0.09,|    0.091, ...]
        #                           ^ pos [50]                    ^ pos+ext [90] + 0.1
        # Both inclusive and exclusive include index 90
        #
        # dim3: [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8,|    1.9]
        #                                 ^ pos [5]          ^ pos+ext [8] + 0.1
        # Both inclusive and exclusive include index 8

        midpoint_tag.references.append(da)

        # all slicing is inclusive since the pos+ext points are between ticks
        slice_default = midpoint_tag.tagged_data(1, 0)
        assert slice_default.shape == (1, 41, 4)
        np.testing.assert_array_equal(slice_default, da[1:2, 50:91, 5:9])

        slice_inclusive = midpoint_tag.tagged_data(1, 0, stop_rule=nix.SliceMode.Inclusive)
        assert slice_inclusive.shape == (2, 41, 4)
        np.testing.assert_array_equal(slice_inclusive, da[1:3, 50:91, 5:9])

        slice_exclusive = midpoint_tag.tagged_data(1, 0, stop_rule=nix.SliceMode.Exclusive)
        assert slice_exclusive.shape == (1, 41, 4)
        np.testing.assert_array_equal(slice_exclusive, da[1:2, 50:91, 5:9])

    def test_tagged_set_dim(self):
        """
        Simple test where the slice can be calculated directly from the position and extent and compared to the original
        data.
        Set dimension slicing.
        """
        nsignals = 10
        data = np.random.random_sample((nsignals, 100))
        da = self.block.create_data_array("data", "data", data=data)
        da.append_set_dimension()
        da.append_sampled_dimension(sampling_interval=1).unit = "s"

        posarray = self.block.create_data_array("mtag.positions", "test.positions", dtype=float, shape=(1,))
        extarray = self.block.create_data_array("mtag.extents", "test.extents", dtype=float, shape=(1,))
        mtag = self.block.create_multi_tag("mtag", "simple", positions=posarray)
        mtag.extents = extarray

        mtag.references.append(da)

        for pos in range(nsignals):
            for ext in range(2, nsignals-pos):
                mtag.positions[:] = [pos]
                mtag.extents[:] = [ext]
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive), da[pos:pos+ext+1])

                # +0.1 should round up (ceil) the start position
                # +0.1 * 2 should round down (floor) the stop position and works the same for both inclusive and
                # exclusive
                mtag.positions[:] = [pos+0.1]
                mtag.extents[:] = [ext+0.1]
                start = pos+1
                stop = pos+ext+1
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[start:stop])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive), da[start:stop])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive), da[start:stop])

                if pos+ext+2 < len(da):
                    # +0.9 should round up (ceil) the start position
                    # +0.9 * 2 should round down (floor) the stop position and works the same for both inclusive and
                    # exclusive
                    mtag.positions[:] = [pos+0.9]
                    mtag.extents[:] = [ext+0.9]
                    start = pos+1
                    stop = pos+ext+2
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[start:stop])
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive),
                                                         da[start:stop])
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive),
                                                         da[start:stop])

    def test_tagged_range_dim(self):
        """
        Simple test where the slice can be calculated directly from the position and extent and compared to the original
        data.
        Range dimension slicing.
        """
        nticks = 10
        data = np.random.random_sample((nticks, 100))
        da = self.block.create_data_array("data", "data", data=data)
        da.append_range_dimension(ticks=range(nticks))
        da.append_sampled_dimension(sampling_interval=1).unit = "s"

        posarray = self.block.create_data_array("mtag.positions", "test.positions", dtype=float, shape=(1,))
        extarray = self.block.create_data_array("mtag.extents", "test.extents", dtype=float, shape=(1,))
        mtag = self.block.create_multi_tag("mtag", "simple", positions=posarray)
        mtag.extents = extarray

        mtag.references.append(da)

        for pos in range(nticks):
            for ext in range(2, nticks-pos):
                mtag.positions[:] = [pos]
                mtag.extents[:] = [ext]
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive), da[pos:pos+ext+1])

                # +0.1 should round up (ceil) the start position
                # +0.1 * 2 should round down (floor) the stop position and works the same for both inclusive and
                # exclusive
                mtag.positions[:] = [pos+0.1]
                mtag.extents[:] = [ext+0.1]
                start = pos+1
                stop = pos+ext+1
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[start:stop])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive), da[start:stop])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive), da[start:stop])

                if pos+ext+2 < len(da):
                    # +0.9 should round up (ceil) the start position
                    # +0.9 * 2 should round down (floor) the stop position and works the same for both inclusive and
                    # exclusive
                    mtag.positions[:] = [pos+0.9]
                    mtag.extents[:] = [ext+0.9]
                    start = pos+1
                    stop = pos+ext+2
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[start:stop])
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive),
                                                         da[start:stop])
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive),
                                                         da[start:stop])

    def test_tagged_sampled_dim(self):
        """
        Simple test where the slice can be calculated directly from the position and extent and compared to the original
        data.
        Sampled dimension slicing.
        """
        nticks = 10
        data = np.random.random_sample((nticks, 100))
        da = self.block.create_data_array("data", "data", data=data)
        da.append_sampled_dimension(sampling_interval=1).unit = "V"
        da.append_sampled_dimension(sampling_interval=1).unit = "s"

        posarray = self.block.create_data_array("mtag.positions", "test.positions", dtype=float, shape=(1,))
        extarray = self.block.create_data_array("mtag.extents", "test.extents", dtype=float, shape=(1,))
        mtag = self.block.create_multi_tag("mtag", "simple", positions=posarray)
        mtag.extents = extarray
        mtag.units = ["V", "s"]

        mtag.references.append(da)

        for pos in range(nticks):
            for ext in range(2, nticks-pos):
                mtag.positions[:] = [pos]
                mtag.extents[:] = [ext]
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive),
                                                     da[pos:pos+ext+1])

                # +0.1 should round up (ceil) the start position
                # +0.1 * 2 should round down (floor) the stop position and works the same for both inclusive and
                # exclusive
                mtag.positions[:] = [pos+0.1]
                mtag.extents[:] = [ext+0.1]
                start = pos+1
                stop = pos+ext+1
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[start:stop])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive), da[start:stop])
                np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive), da[start:stop])

                if pos+ext+2 < len(da):
                    # +0.9 should round up (ceil) the start position
                    # +0.9 * 2 should round down (floor) the stop position and works the same for both inclusive and
                    # exclusive
                    mtag.positions[:] = [pos+0.9]
                    mtag.extents[:] = [ext+0.9]
                    start = pos+1
                    stop = pos+ext+2
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0), da[start:stop])
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Exclusive),
                                                         da[start:stop])
                    np.testing.assert_array_almost_equal(mtag.tagged_data(0, 0, nix.SliceMode.Inclusive),
                                                         da[start:stop])
