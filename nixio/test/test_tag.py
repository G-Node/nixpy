# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
import time
import unittest
from collections import OrderedDict
import numpy as np
import nixio as nix
from nixio.exceptions import UnsupportedLinkType
from .tmp import TempDir


class TestTags(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("tagtest")
        self.testfilename = os.path.join(self.tmpdir.path, "tagtest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")

        self.my_array = self.block.create_data_array("my array", "test",
                                                     nix.DataType.Int16, (1,))
        self.my_tag = self.block.create_tag(
            "my tag", "tag", [0]
        )
        self.my_tag.references.append(self.my_array)

        self.your_array = self.block.create_data_array(
            "your array", "test", nix.DataType.Int16, (1,)
        )
        self.your_tag = self.block.create_tag(
            "your tag", "tag", [0]
        )
        self.your_tag.references.append(self.your_array)

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_flex(self):
        tag1d = self.block.create_tag("1dim tag", "tag", [1])
        tag2d = self.block.create_tag("2dim tag", "tag", [1, 1])
        tag3d = self.block.create_tag("3dim tag", "tag", [1, 1, 1])
        da1d = self.block.create_data_array("1d array", "da",
                                            data=np.arange(5))
        da1d.append_sampled_dimension(1., label="time", unit="s")
        da2d = self.block.create_data_array("2d array", "da",
                                            data=np.arange(25).reshape((5, 5)))
        da2d.append_sampled_dimension(1., label="time", unit="s")
        da2d.append_set_dimension()
        da3d = self.block.create_data_array("3d array", "da",
                                            data=np.arange(125)
                                            .reshape((5, 5, 5)))
        da3d.append_sampled_dimension(1., label="time", unit="s")
        da3d.append_set_dimension()
        da3d.append_set_dimension()
        tag1d.extent = [1]
        tag1d.references.extend([da1d, da2d, da3d])
        assert list(tag1d.references) == [da1d, da2d, da3d]
        ref1 = tag1d.tagged_data(1)  # 1d tag to 2d data
        for (ref_val, da_val) in zip(ref1[:].flatten(), da2d[1:3, :].flatten()):
            assert ref_val == da_val
        tag2d.extent = [1, 2]
        tag2d.references.extend([da1d, da2d, da3d])
        tag2d.tagged_data(0)  # 2d tag to 1d data
        tag3d.extent = [1, 2, 3]
        tag3d.references.extend([da1d, da2d, da3d])
        np.testing.assert_array_equal(tag3d.tagged_data(0), da1d[1:2])
        np.testing.assert_array_equal(tag3d.tagged_data(1), da2d[1:2, 1:3])
        np.testing.assert_array_equal(tag3d.tagged_data(2), da3d[1:2, 1:3, 1:4])

    def test_tag_eq(self):
        assert self.my_tag == self.my_tag
        assert not self.my_tag == self.your_tag
        assert self.my_tag is not None

    def test_tag_id(self):
        assert self.my_tag.id is not None

    def test_tag_name(self):
        assert self.my_tag.name is not None

    def test_tag_type(self):
        def set_none():
            self.my_tag.type = None

        assert self.my_tag.type is not None
        self.assertRaises(Exception, set_none)

        self.my_tag.type = "foo type"
        assert self.my_tag.type == "foo type"

    def test_tag_definition(self):
        assert self.my_tag.definition is None

        self.my_tag.definition = "definition"
        assert self.my_tag.definition == "definition"

        self.my_tag.definition = None
        assert self.my_tag.definition is None

    def test_tag_timestamps(self):
        created_at = self.my_tag.created_at
        assert created_at > 0

        updated_at = self.my_tag.updated_at
        assert updated_at > 0

        self.my_tag.force_created_at(1403530068)
        assert self.my_tag.created_at == 1403530068

    def test_tag_units(self):
        assert self.my_tag.units == ()

        self.my_tag.units = ["mV", "ms"]
        assert self.my_tag.units == ("mV", "ms")

        self.my_tag.units = []
        assert self.my_tag.units == ()

    def test_tag_position(self):
        assert self.my_tag.position == (0,)

        self.my_tag.position = (1.0, 2.0, 3.0)
        assert self.my_tag.position == (1.0, 2.0, 3.0)

    def test_tag_extent(self):
        assert self.my_tag.extent == ()

        self.my_tag.extent = (1.0, 2.0, 3.0)
        assert self.my_tag.extent == (1.0, 2.0, 3.0)

        self.my_tag.extent = []
        assert self.my_tag.extent == ()

    def test_tag_references(self):
        assert len(self.my_tag.references) == 1

        self.assertRaises(TypeError, self.my_tag.references.append, 100)

        reference1 = self.block.create_data_array("reference1", "stimuli",
                                                  nix.DataType.Int16, (1,))
        reference2 = self.block.create_data_array("reference2", "stimuli",
                                                  nix.DataType.Int16, (1,))

        self.my_tag.references.append(reference1)
        self.my_tag.references.append(reference2)

        assert reference1.name in self.my_tag.references

        assert len(self.my_tag.references) == 3
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
        assert self.my_array in self.my_tag.references
        assert reference1 in self.my_tag.references

        del self.my_tag.references[reference1]
        assert len(self.my_tag.references) == 1

    def test_tag_features(self):
        assert len(self.my_tag.features) == 0

        data_array = self.block.create_data_array("feature", "stimuli",
                                                  nix.DataType.Int16, (1,))
        da_feature = self.my_tag.create_feature(data_array, nix.LinkType.Untagged)

        assert len(self.my_tag.features) == 1

        assert da_feature in self.my_tag.features
        assert da_feature.id in self.my_tag.features
        assert "notexist" not in self.my_tag.features

        assert da_feature.id == self.my_tag.features[0].id
        assert da_feature.id == self.my_tag.features[-1].id

        # id and name access
        assert da_feature.id == self.my_tag.features[da_feature.id].id
        assert da_feature.id == self.my_tag.features[data_array.id].id
        assert da_feature.id == self.my_tag.features[data_array.name].id
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

    def test_tag_tagged_data(self):
        sample_iv = 1.0
        ticks = [1.2, 2.3, 3.4, 4.5, 6.7]
        unit = "ms"
        pos = [0.0, 2.0, 3.4]
        ext = [0.1, 6.0, 2.3]
        units = ["none", "ms", "ms"]
        data = np.random.random_sample((2, 10, 5))
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

        posdata = postag.tagged_data(0)
        assert len(posdata.shape) == 3
        assert posdata.shape == (1, 1, 1)

        segdata = segtag.tagged_data(0)
        assert len(segdata.shape) == 3
        assert segdata.shape == (1, 6, 2)

        # retrieve data by id and name
        posdata = postag.tagged_data(da.name)
        assert len(posdata.shape) == 3
        assert posdata.shape == (1, 1, 1)
        segdata = segtag.tagged_data(da.name)
        assert len(segdata.shape) == 3
        assert segdata.shape == (1, 6, 2)

        posdata = postag.tagged_data(da.id)
        assert len(posdata.shape) == 3
        assert posdata.shape == (1, 1, 1)
        segdata = segtag.tagged_data(da.id)
        assert len(segdata.shape) == 3
        assert segdata.shape == (1, 6, 2)

    def test_tag_tagged_data_slice_mode(self):
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
        exact_tag = self.block.create_tag("tickpoint", "test.tag", position=[0, 0.03, 0.0011])
        exact_tag.extent = [0.2, 0.02, 0.0005]
        exact_tag.units = ["none", "s", "m"]

        exact_tag.references.append(da)

        # dim2: [0.001, 0.002, ..., 0.03, 0.031, ..., 0.049, 0.05, 0.051, ...]
        #                           ^ pos [30]               ^ pos+ext [50]
        # Inclusive mode includes index 50, exclusive does not
        #
        # dim3: [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]
        #             ^ pos [1]                ^ pos+ext [6]
        # Inclusive mode includes index 6, exclusive does not

        slice_default = exact_tag.tagged_data(0)
        assert slice_default.shape == (1, 20, 5)
        np.testing.assert_array_equal(slice_default, da[0:1, 30:50, 1:6])  # default exclusive

        slice_inclusive = exact_tag.tagged_data(0, stop_rule=nix.SliceMode.Inclusive)
        assert slice_inclusive.shape == (1, 21, 6)
        np.testing.assert_array_equal(slice_inclusive, da[0:1, 30:51, 1:7])

        slice_exclusive = exact_tag.tagged_data(0, stop_rule=nix.SliceMode.Exclusive)
        assert slice_exclusive.shape == (1, 20, 5)
        np.testing.assert_array_equal(slice_exclusive, da[0:1, 30:50, 1:6])

        # midpoint_tag has a pos+ext that falls between dimension ticks
        midpoint_tag = self.block.create_tag("midpoint", "test.tag", position=[0, 0.03, 0.0011])
        midpoint_tag.extent = [0.1, 0.0301, 0.00051]  # .1 offset
        midpoint_tag.units = ["none", "s", "m"]

        # dim2: [0.001, 0.002, ..., 0.03, 0.031, ..., 0.059, 0.06,|   0.061, ...]
        #                           ^ pos [30]                    ^ pos+ext [60] + 0.1
        # Both inclusive and exclusive include index 60
        #
        # dim3: [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6,|   1.7, 1.8, 1.9]
        #             ^ pos [1]                    ^ pos+ext [6] + 0.1
        # Both inclusive and exclusive include index 6

        midpoint_tag.references.append(da)

        # all slicing is inclusive since the pos+ext points are between ticks
        slice_default = midpoint_tag.tagged_data(0)
        assert slice_default.shape == (1, 31, 6)
        np.testing.assert_array_equal(slice_default, da[0:1, 30:61, 1:7])

        slice_inclusive = midpoint_tag.tagged_data(0, stop_rule=nix.SliceMode.Inclusive)
        assert slice_inclusive.shape == (1, 31, 6)
        np.testing.assert_array_equal(slice_inclusive, da[0:1, 30:61, 1:7])

        slice_exclusive = midpoint_tag.tagged_data(0, stop_rule=nix.SliceMode.Exclusive)
        assert slice_exclusive.shape == (1, 31, 6)
        np.testing.assert_array_equal(slice_exclusive, da[0:1, 30:61, 1:7])

    def test_tag_feature_data(self):
        number_data = np.random.random(20)
        number_feat = self.block.create_data_array("number feature", "test",
                                                   data=number_data)
        dim = number_feat.append_sampled_dimension(1.0)
        dim.unit = "ms"
        dim.offset = 1.0

        ramp_data = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        ramp_feat = self.block.create_data_array("ramp feature", "test",
                                                 data=np.asarray(ramp_data))
        ramp_feat.label = "voltage"
        ramp_feat.unit = "mV"
        dim = ramp_feat.append_sampled_dimension(1.0)
        dim.unit = "ms"
        dim.offset = 2.0

        pos_tag = self.block.create_tag("feature test", "test", [5.0])
        pos_tag.units = ["ms"]

        pos_tag.create_feature(number_feat, nix.LinkType.Tagged)
        pos_tag.create_feature(number_feat, nix.LinkType.Untagged)
        pos_tag.create_feature(number_feat, nix.LinkType.Indexed)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Tagged)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Untagged)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Indexed)
        assert len(pos_tag.features) == 6

        data1 = pos_tag.feature_data(0)
        data2 = pos_tag.feature_data(1)
        data3 = pos_tag.feature_data(2)
        data4 = pos_tag.feature_data(3)
        data5 = pos_tag.feature_data(4)
        data6 = pos_tag.feature_data(5)

        assert data1.size == 1
        assert data2.size == len(number_data)
        assert data3.size == len(number_data)
        assert data4.size == 1
        assert data5.size == len(ramp_data)
        assert data6.size == len(ramp_data)

        # check expected data
        # For Tag, both Indexed and Untagged just return the full data
        assert np.all(data1[:] == number_data[4:5])
        assert np.all(data2[:] == number_data[:])
        assert np.all(data3[:] == number_data[:])
        assert np.all(data4[:] == ramp_data[3:4])
        assert np.all(data5[:] == ramp_data[:])
        assert np.all(data6[:] == ramp_data[:])

        # make the tag pointing to a slice
        pos_tag.extent = [2.0]
        data1 = pos_tag.feature_data(0)
        data2 = pos_tag.feature_data(1)
        data3 = pos_tag.feature_data(2)
        data4 = pos_tag.feature_data(3)
        data5 = pos_tag.feature_data(4)
        data6 = pos_tag.feature_data(5)

        assert np.all(data1[:] == number_data[4:6])
        assert np.all(data2[:] == number_data[:])
        assert np.all(data3[:] == number_data[:])
        assert np.all(data4[:] == ramp_data[3:5])
        assert np.all(data5[:] == ramp_data[:])
        assert np.all(data6[:] == ramp_data[:])

    def test_tag_feature_dataframe(self):
        numberdata = np.random.random(20)
        number_feat = self.block.create_data_frame(
            "number feature", "test",
            col_dict=OrderedDict([("number", nix.DataType.Float)]),
            data=[(n,) for n in numberdata]
        )
        column_descriptions = OrderedDict([("name", nix.DataType.String), ("duration", nix.DataType.Double)])
        values = [("One", 0.1), ("Two", 0.2), ("Three", 0.3), ("Four", 0.4), ("Five", 0.5),
                  ("Six", 0.6), ("Seven", 0.7), ("Eight", 0.8), ("Nine", 0.9), ("Ten", 1.0)]
        ramp_feat = self.block.create_data_frame("ramp feature", "test", col_dict=column_descriptions, data=values)
        ramp_feat.label = "voltage"
        ramp_feat.units = (None, "s")

        pos_tag = self.block.create_tag("feature test", "test", [5.0])

        with self.assertRaises(UnsupportedLinkType):
            pos_tag.create_feature(number_feat, nix.LinkType.Tagged)
        pos_tag.create_feature(number_feat, nix.LinkType.Untagged)
        pos_tag.create_feature(number_feat, nix.LinkType.Indexed)
        with self.assertRaises(UnsupportedLinkType):
            pos_tag.create_feature(ramp_feat, nix.LinkType.Tagged)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Untagged)
        pos_tag.create_feature(ramp_feat, nix.LinkType.Indexed)
        assert len(pos_tag.features) == 4

        data1 = pos_tag.feature_data(0)
        data2 = pos_tag.feature_data(1)
        data3 = pos_tag.feature_data(2)
        data4 = pos_tag.feature_data(3)

        # check expected data
        # For Tag, both Indexed and Untagged just return the full data
        assert np.all(data1[:] == number_feat[:])
        assert np.all(data2[:] == number_feat[:])
        assert np.all(data3[:] == ramp_feat[:])
        assert np.all(data4[:] == ramp_feat[:])

        # Extent should have no effect
        pos_tag.extent = [2.0]
        data1 = pos_tag.feature_data(0)
        data2 = pos_tag.feature_data(1)
        data3 = pos_tag.feature_data(2)
        data4 = pos_tag.feature_data(3)

        assert np.all(data1[:] == number_feat[:])
        assert np.all(data2[:] == number_feat[:])
        assert np.all(data3[:] == ramp_feat[:])
        assert np.all(data4[:] == ramp_feat[:])

    def test_timestamp_autoupdate(self):
        tag = self.block.create_tag("tag.time", "test.time", [-1])

        tagtime = tag.updated_at
        time.sleep(1)  # wait for time to change
        tag.position = [-100]
        self.assertNotEqual(tag.updated_at, tagtime)

        tagtime = tag.updated_at
        time.sleep(1)  # wait for time to change
        tag.extent = [30]
        self.assertNotEqual(tag.updated_at, tagtime)

        tagtime = tag.updated_at
        time.sleep(1)  # wait for time to change
        tag.units = "Mm"
        self.assertNotEqual(tag.updated_at, tagtime)

    def test_timestamp_noautoupdate(self):
        self.file.auto_update_timestamps = False
        tag = self.block.create_tag("tag.time", "test.time", [-1])

        tagtime = tag.updated_at
        time.sleep(1)  # wait for time to change
        tag.position = [-100]
        self.assertEqual(tag.updated_at, tagtime)

        tagtime = tag.updated_at
        time.sleep(1)  # wait for time to change
        tag.extent = [30]
        self.assertEqual(tag.updated_at, tagtime)

        tagtime = tag.updated_at
        time.sleep(1)  # wait for time to change
        tag.units = "Mm"
        self.assertEqual(tag.updated_at, tagtime)

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

        tag = self.block.create_tag("tag", "simple", position=[])

        tag.references.append(da)

        for pos in range(nsignals):
            for ext in range(2, nsignals-pos):
                tag.position = [pos]
                tag.extent = [ext]
                np.testing.assert_array_almost_equal(tag.tagged_data(0), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[pos:pos+ext+1])

                # +0.1 should round up (ceil) the start position
                # +0.1 * 2 should round down (floor) the stop position and works the same for both inclusive and
                # exclusive
                tag.position = [pos+0.1]
                tag.extent = [ext+0.1]
                start = pos+1
                stop = pos+ext+1
                np.testing.assert_array_almost_equal(tag.tagged_data(0), da[start:stop])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[start:stop])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[start:stop])

                if pos+ext+2 < len(da):
                    # +0.9 should round up (ceil) the start position
                    # +0.9 *2 should round down (floor) the stop position and works the same for both inclusive and
                    # exclusive
                    tag.position = [pos+0.9]
                    tag.extent = [ext+0.9]
                    start = pos+1
                    stop = pos+ext+2
                    np.testing.assert_array_almost_equal(tag.tagged_data(0), da[start:stop])
                    np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[start:stop])
                    np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[start:stop])

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

        tag = self.block.create_tag("tag", "simple", position=[])

        tag.references.append(da)

        for pos in range(nticks):
            for ext in range(2, nticks-pos):
                tag.position = [pos]
                tag.extent = [ext]
                np.testing.assert_array_almost_equal(tag.tagged_data(0), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[pos:pos+ext+1])

                # +0.1 should round up (ceil) the start position
                # +0.1 * 2 should round down (floor) the stop position and works the same for both inclusive and
                # exclusive
                tag.position = [pos + 0.1]
                tag.extent = [ext + 0.1]
                start = pos + 1
                stop = pos + ext + 1
                np.testing.assert_array_almost_equal(tag.tagged_data(0), da[start:stop])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[start:stop])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[start:stop])

                if pos + ext + 2 < len(da):
                    # +0.9 should round up (ceil) the start position
                    # +0.9 * 2 should round down (floor) the stop position and works the same for both inclusive and
                    # exclusive
                    tag.position = [pos + 0.9]
                    tag.extent = [ext + 0.9]
                    start = pos + 1
                    stop = pos + ext + 2
                    np.testing.assert_array_almost_equal(tag.tagged_data(0), da[start:stop])
                    np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[start:stop])
                    np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[start:stop])

        time_vector = np.arange(0.0, 10., 0.001)
        indices = np.random.rand(len(time_vector))
        event_data = time_vector[(indices < 0.1)]
        event_data = event_data[(event_data < 4) | (event_data > 7)]

        event_da = self.block.create_data_array("event_data", "nix.events", data=event_data, unit="s")
        event_da.append_range_dimension_using_self()
        selection = event_da.get_slice([4.5], [1.0], nix.DataSliceMode.Data)[:]

        tt = self.block.create_tag("no_event_segment", "nix.segment", 4.5)
        tt.extent = 1.0
        tt.references.append(event_da)
        slice = tt.tagged_data(0)
        self.assertFalse(slice.valid)

        tt2 = self.block.create_tag("beyond data", "nix.segment", 12.0)
        tt2.extent = 3.0
        tt2.references.append(event_da)
        slice = tt2.tagged_data(0)
        self.assertFalse(slice.valid)

        tt3 = self.block.create_tag("reachingbeyonddata", "nix.segment", 8.5)
        tt3.extent = [3.0]
        tt3.references.append(event_da)
        slice = tt3.tagged_data(0)
        self.assertTrue(slice.valid)

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

        tag = self.block.create_tag("tag", "simple", position=[])
        tag.units = ["V", "s"]

        tag.references.append(da)

        for pos in range(nticks):
            for ext in range(2, nticks-pos):
                tag.position = [pos]
                tag.extent = [ext]
                np.testing.assert_array_almost_equal(tag.tagged_data(0), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[pos:pos+ext])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[pos:pos+ext+1])

                # +0.1 should round up (ceil) the start position
                # +0.1 * 2 should round down (floor) the stop position and works the same for both inclusive and
                # exclusive
                tag.position = [pos+0.1]
                tag.extent = [ext+0.1]
                start = pos+1
                stop = pos+ext+1
                np.testing.assert_array_almost_equal(tag.tagged_data(0), da[start:stop])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[start:stop])
                np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[start:stop])

                if pos+ext+2 < len(da):
                    # +0.9 should round up (ceil) the start position
                    # +0.9 * 2 should round down (floor) the stop position and works the same for both inclusive and
                    # exclusive
                    tag.position = [pos+0.9]
                    tag.extent = [ext+0.9]
                    start = pos+1
                    stop = pos+ext+2
                    np.testing.assert_array_almost_equal(tag.tagged_data(0), da[start:stop])
                    np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Exclusive), da[start:stop])
                    np.testing.assert_array_almost_equal(tag.tagged_data(0, nix.SliceMode.Inclusive), da[start:stop])
