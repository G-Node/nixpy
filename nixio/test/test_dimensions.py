# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from nixio.dimensions import RangeMode
from nixio.exceptions.exceptions import IncompatibleDimensions
import os
import unittest
import numpy as np

import nixio as nix
from .tmp import TempDir
from collections import OrderedDict


TEST_SAMPL = 0.1
TEST_LABEL = "test label"
test_range = tuple([float(i) for i in range(10)])
test_labels = tuple([str(i) + "_label" for i in range(10)])


class TestDimension(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("dimtest")
        self.testfilename = os.path.join(self.tmpdir.path, "dimtest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.array = self.block.create_data_array("test array", "signal",
                                                  nix.DataType.Float, (0, ))

        self.set_dim = self.array.append_set_dimension()
        self.sample_dim = self.array.append_sampled_dimension(TEST_SAMPL)
        self.range_dim = self.array.append_range_dimension(test_range)

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_set_dimension(self):
        assert self.set_dim.index == 1
        assert self.set_dim.dimension_type == nix.DimensionType.Set
        assert self.array.dimensions[0].index == 1

        assert self.set_dim.labels == ()
        self.set_dim.labels = test_labels
        assert self.set_dim.labels == test_labels

        assert self.set_dim.label is None
        self.set_dim.label = TEST_LABEL
        assert self.set_dim.label == TEST_LABEL
        self.set_dim.label = None
        assert self.set_dim.label is None

    def test_sample_dimension(self):
        assert self.sample_dim.index == 2
        assert self.sample_dim.dimension_type == nix.DimensionType.Sample
        assert self.array.dimensions[1].index == 2

        assert self.sample_dim.label is None
        self.sample_dim.label = TEST_LABEL
        assert self.sample_dim.label == TEST_LABEL
        self.sample_dim.label = None
        assert self.sample_dim.label is None

        assert self.sample_dim.unit is None
        self.sample_dim.unit = "mV"
        assert self.sample_dim.unit == "mV"
        self.sample_dim.unit = None
        assert self.sample_dim.unit is None

        assert self.sample_dim.sampling_interval == TEST_SAMPL
        self.sample_dim.sampling_interval = 1.123
        assert self.sample_dim.sampling_interval == 1.123

        assert self.sample_dim.offset is None
        self.sample_dim.offset = 0.3
        assert self.sample_dim.offset == 0.3
        self.sample_dim.offset = None
        assert self.sample_dim.offset is None

        self.sample_dim.sampling_interval = 2.
        self.sample_dim.offset = 3.

        assert self.sample_dim.index_of(3.14) == 0
        assert self.sample_dim.index_of(23.) == 10
        assert type(self.sample_dim.index_of(23.) == int)

        assert self.sample_dim.position_at(0) == 3.
        assert self.sample_dim.position_at(200) == 200 * 2. + 3.

        assert len(self.sample_dim.axis(10)) == 10
        assert self.sample_dim.axis(10)[0] == 3.
        assert self.sample_dim.axis(10)[-1] == 9 * 2. + 3.

        assert len(self.sample_dim.axis(10, 2)) == 10
        assert self.sample_dim.axis(10, 2)[0] == 2 * 2. + 3.
        assert self.sample_dim.axis(10, 2)[-1] == (9 + 2) * 2. + 3.

        with self.assertRaises(ValueError):
            self.sample_dim.axis(10, -10)
            self.sample_dim.axis(10, start_position=0.0)
        assert self.sample_dim.axis(10, 0, 5.0)[0] == 3
        assert self.sample_dim.axis(10, start_position=5.0)[0] == 5.0
        assert self.sample_dim.axis(10, start_position=5.0)[-1] == 5.0 + 9 * 2

        with self.assertRaises(ValueError):
            self.sample_dim.range_indices(0, 1, mode="invalid")
        with self.assertRaises(IndexError):
            self.sample_dim.range_indices(10, -10, mode=RangeMode.Inclusive)
        range_indices = self.sample_dim.range_indices(2, 11, mode=RangeMode.Inclusive)
        assert range_indices[0] == 0
        assert range_indices[-1] == 4

        range_indices = self.sample_dim.range_indices(2, 11, mode=RangeMode.Exclusive)
        assert range_indices[0] == 0
        assert range_indices[-1] == 3

        range_indices = self.sample_dim.range_indices(3., 3.1, mode=RangeMode.Inclusive)
        assert range_indices[0] == 0
        assert range_indices[-1] == 0
        range_indices = self.sample_dim.range_indices(3., 3.1, mode=RangeMode.Exclusive)
        assert range_indices[0] == 0
        assert range_indices[-1] == 0

        range_indices = self.sample_dim.range_indices(3.1, 3.2, mode=RangeMode.Inclusive)
        self.assertIsNone(range_indices)
        range_indices = self.sample_dim.range_indices(3.1, 3.2, mode=RangeMode.Exclusive)
        self.assertIsNone(range_indices)

        range_indices = self.sample_dim.range_indices(3.1, 5.0, mode=RangeMode.Inclusive)
        self.assertIsNotNone(range_indices)
        range_indices = self.sample_dim.range_indices(3.1, 5.0, mode=RangeMode.Exclusive)
        self.assertIsNone(range_indices)

    def test_range_dimension(self):
        assert self.range_dim.index == 3
        assert self.range_dim.dimension_type == nix.DimensionType.Range
        assert self.array.dimensions[2].index == 3

        assert self.range_dim.label is None
        self.range_dim.label = TEST_LABEL
        assert self.range_dim.label == TEST_LABEL
        self.range_dim.label = None
        assert self.range_dim.label is None

        assert self.range_dim.unit is None
        self.range_dim.unit = "mV"
        assert self.range_dim.unit == "mV"
        self.range_dim.unit = None
        assert self.range_dim.unit is None

        assert self.range_dim.ticks == test_range
        other = tuple([i * 3.14 for i in range(10)])
        self.range_dim.ticks = other
        assert self.range_dim.ticks == other

        assert self.range_dim.index_of(0.) == 0
        assert self.range_dim.index_of(10.) == (np.floor(10. / 3.14))
        assert self.range_dim.index_of(18.84) == 6
        assert self.range_dim.index_of(28.26) == 9
        assert self.range_dim.index_of(100.) == 9
        assert self.range_dim.index_of(-100., mode=nix.IndexMode.GreaterOrEqual) == 0

        assert self.range_dim.tick_at(0) == 0
        assert self.range_dim.tick_at(9) == other[-1]
        with self.assertRaises(IndexError):
            self.range_dim.tick_at(100)

        assert self.range_dim.axis(10) == other
        assert self.range_dim.axis(2) == other[:2]
        assert self.range_dim.axis(2, 2) == other[2:4]
        with self.assertRaises(IndexError):
            self.range_dim.axis(10, 2)
            self.range_dim.axis(100)

        #  ticks = (0.0, 3.14, 6.28, 9.42, 12.56, 15.7, 18.84, 21.98, 25.12, 28.26)
        with self.assertRaises(ValueError):
            self.range_dim.range_indices(0, 10, mode="invalid")
        with self.assertRaises(IndexError):
            self.range_dim.range_indices(10, -10)

        self.assertIsNone(self.range_dim.range_indices(3.15, 3.16, mode=RangeMode.Inclusive))
        self.assertIsNone(self.range_dim.range_indices(3.15, 3.16, mode=RangeMode.Exclusive))

        range_indices = self.range_dim.range_indices(3.14, 4.0, mode=RangeMode.Inclusive)
        assert range_indices[0] == 1
        assert range_indices[1] == 1
        range_indices = self.range_dim.range_indices(3.14, 4.0, mode=RangeMode.Exclusive)
        assert range_indices[0] == 1
        assert range_indices[1] == 1

        range_indices = self.range_dim.range_indices(6.2, 25.12, mode=RangeMode.Inclusive)
        assert range_indices[0] == 2
        assert range_indices[1] == 8
        range_indices = self.range_dim.range_indices(6.2, 25.12, mode=RangeMode.Exclusive)
        assert range_indices[0] == 2
        assert range_indices[1] == 7

    def test_set_dim_label_resize(self):
        setdim = self.array.append_set_dimension()
        labels = ["A", "B"]
        setdim.labels = labels
        assert tuple(labels) == setdim.labels

        newlabels = ["C", "B", "A"]
        setdim.labels = newlabels
        assert tuple(newlabels) == setdim.labels

    def test_set_dim_labels_array(self):
        labels = np.array(["A", "B"])
        setdim = self.array.append_set_dimension(labels)
        assert tuple(labels) == setdim.labels

    def test_set_dim_invalid_labels(self):
        # don't accept non list-like labels
        with self.assertRaises(ValueError):
            self.array.append_set_dimension('Sample 1')
        with self.assertRaises(ValueError):
            self.array.append_set_dimension(1000)

        # don't accept list of non-string objects
        with self.assertRaises(ValueError):
            self.array.append_set_dimension([1, 2, 3])

    def test_range_dim_ticks_resize(self):
        rangedim = self.array.append_range_dimension([1, 2, 100])
        ticks = [1, 1, 30]
        rangedim.ticks = ticks
        assert tuple(ticks) == rangedim.ticks

        newticks = [2, 4, 300, 800]
        rangedim.ticks = newticks
        assert tuple(newticks) == rangedim.ticks

    def test_append_dim_init(self):
        slabels = ["label A", "label B"]
        setdim = self.array.append_set_dimension(slabels)
        assert tuple(slabels) == setdim.labels

        rticks = [1, 2, 10.3]
        rlabel = "range-label"
        runit = "ms"
        rdim = self.array.append_range_dimension(rticks, rlabel, runit)
        assert tuple(rticks) == rdim.ticks
        assert rlabel == rdim.label
        assert runit == rdim.unit

        sinterval = 0.25
        slabel = "sample label"
        sunit = "us"
        soffset = 10
        smpldim = self.array.append_sampled_dimension(sinterval,
                                                      slabel,
                                                      sunit,
                                                      soffset)
        assert sinterval == smpldim.sampling_interval
        assert slabel == smpldim.label
        assert sunit == smpldim.unit
        assert soffset == smpldim.offset

    def test_set_dimension_modes(self):
        # exact
        assert self.set_dim.index_of(0) == 0
        assert self.set_dim.index_of(0, nix.IndexMode.LessOrEqual) == 0
        assert self.set_dim.index_of(0, nix.IndexMode.GreaterOrEqual) == 0
        assert self.set_dim.index_of(7) == 7
        assert self.set_dim.index_of(7, nix.IndexMode.LessOrEqual) == 7
        assert self.set_dim.index_of(7, nix.IndexMode.LessOrEqual) == 7
        assert self.set_dim.index_of(7, nix.IndexMode.GreaterOrEqual) == 7
        assert self.set_dim.index_of(7, nix.IndexMode.Less) == 6

        # rounding
        assert self.set_dim.index_of(4.2) == 4
        assert self.set_dim.index_of(4.2, nix.IndexMode.LessOrEqual) == 4
        assert self.set_dim.index_of(4.2, nix.IndexMode.Less) == 4
        assert self.set_dim.index_of(4.2, nix.IndexMode.GreaterOrEqual) == 5

        # valid oob below
        assert self.set_dim.index_of(-30, nix.IndexMode.GreaterOrEqual) == 0

        self.set_dim.labels = test_labels
        # valid oob above
        assert self.set_dim.index_of(12989) == len(test_labels) - 1
        assert self.set_dim.index_of(12989, nix.IndexMode.LessOrEqual) == len(test_labels) - 1
        assert self.set_dim.index_of(12989, nix.IndexMode.Less) == len(test_labels) - 1

        # invalid oob
        with self.assertRaises(IndexError):
            self.set_dim.index_of(0, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.set_dim.index_of(-1, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.set_dim.index_of(-10, nix.IndexMode.LessOrEqual)
        with self.assertRaises(IndexError):
            self.set_dim.index_of(-10)
        with self.assertRaises(IndexError):
            self.set_dim.index_of(12398, nix.IndexMode.GreaterOrEqual)
        with self.assertRaises(IndexError):
            self.set_dim.index_of(len(test_labels) - 0.5, nix.IndexMode.GreaterOrEqual)

        with self.assertRaises(ValueError):
            self.set_dim.range_indices(0, 10, mode="invalid")
        with self.assertRaises(IndexError):
            self.set_dim.range_indices(10, -10)

        range_indices = self.set_dim.range_indices(0.1, 0.4, mode=RangeMode.Inclusive)
        self.assertIsNone(range_indices)
        range_indices = self.set_dim.range_indices(0.1, 0.4, mode=RangeMode.Exclusive)
        self.assertIsNone(range_indices)

        range_indices = self.set_dim.range_indices(0.1, 1.0, mode=RangeMode.Inclusive)
        self.assertIsNotNone(range_indices)
        assert range_indices[0] == 1
        assert range_indices[1] == 1
        range_indices = self.set_dim.range_indices(0.1, 1.0, mode=RangeMode.Exclusive)
        self.assertIsNone(range_indices)
        range_indices = self.set_dim.range_indices(0.1, 1.1, mode=RangeMode.Exclusive)
        self.assertIsNotNone(range_indices)
        assert range_indices[0] == 1
        assert range_indices[1] == 1
        range_indices = self.set_dim.range_indices(0, 9, mode=RangeMode.Exclusive)
        assert range_indices[0] == 0
        assert range_indices[-1] == 8
        range_indices = self.set_dim.range_indices(0, 9, mode=RangeMode.Inclusive)
        assert range_indices[0] == 0
        assert range_indices[-1] == 9

    def test_sampled_dimension_modes(self):
        # exact
        assert self.sample_dim.index_of(0) == 0
        assert self.sample_dim.index_of(0, nix.IndexMode.LessOrEqual) == 0
        assert self.sample_dim.index_of(0, nix.IndexMode.GreaterOrEqual) == 0
        assert self.sample_dim.index_of(7.2) == 72
        assert self.sample_dim.index_of(7.2, nix.IndexMode.LessOrEqual) == 72
        assert self.sample_dim.index_of(7.2, nix.IndexMode.LessOrEqual) == 72
        assert self.sample_dim.index_of(7.2, nix.IndexMode.GreaterOrEqual) == 72
        assert self.sample_dim.index_of(7.2, nix.IndexMode.Less) == 71
        assert self.sample_dim.index_of(7.3, nix.IndexMode.Less) == 72

        # rounding
        assert self.sample_dim.index_of(4.205) == 42
        assert self.sample_dim.index_of(4.205, nix.IndexMode.LessOrEqual) == 42
        assert self.sample_dim.index_of(4.205, nix.IndexMode.Less) == 42
        assert self.sample_dim.index_of(4.205, nix.IndexMode.GreaterOrEqual) == 43

        # valid oob below
        assert self.sample_dim.index_of(-30, nix.IndexMode.GreaterOrEqual) == 0

        # invalid oob
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(0, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(-0.001, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(-1, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(-10, nix.IndexMode.LessOrEqual)
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(-10)

        # with offset
        offset = 3.1
        self.sample_dim.offset = offset

        # valid oob below
        assert self.sample_dim.index_of(-30, nix.IndexMode.GreaterOrEqual) == 0
        assert self.sample_dim.index_of(offset - 0.3, nix.IndexMode.GreaterOrEqual) == 0

        # invalid oob
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(offset - 0.2, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(0, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(offset - 0.01, nix.IndexMode.LessOrEqual)
        with self.assertRaises(IndexError):
            self.sample_dim.index_of(offset - 0.5)

    def test_range_dimension_modes(self):
        # exact
        assert self.range_dim.index_of(0) == 0
        assert self.range_dim.index_of(0, nix.IndexMode.LessOrEqual) == 0
        assert self.range_dim.index_of(0, nix.IndexMode.GreaterOrEqual) == 0
        assert self.range_dim.index_of(7) == 7
        assert self.range_dim.index_of(7, nix.IndexMode.LessOrEqual) == 7
        assert self.range_dim.index_of(7, nix.IndexMode.LessOrEqual) == 7
        assert self.range_dim.index_of(7, nix.IndexMode.GreaterOrEqual) == 7
        assert self.range_dim.index_of(7, nix.IndexMode.Less) == 6

        # rounding
        assert self.range_dim.index_of(4.2) == 4
        assert self.range_dim.index_of(4.2, nix.IndexMode.LessOrEqual) == 4
        assert self.range_dim.index_of(4.2, nix.IndexMode.Less) == 4
        assert self.range_dim.index_of(4.2, nix.IndexMode.GreaterOrEqual) == 5

        # valid oob below
        assert self.range_dim.index_of(-30, nix.IndexMode.GreaterOrEqual) == 0

        # valid oob above
        assert self.range_dim.index_of(12989) == test_range[-1]
        assert self.range_dim.index_of(12989, nix.IndexMode.LessOrEqual) == test_range[-1]
        assert self.range_dim.index_of(12989, nix.IndexMode.Less) == test_range[-1]

        # invalid oob
        with self.assertRaises(IndexError):
            self.range_dim.index_of(0, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.range_dim.index_of(-1, nix.IndexMode.Less)
        with self.assertRaises(IndexError):
            self.range_dim.index_of(-10, nix.IndexMode.LessOrEqual)
        with self.assertRaises(IndexError):
            self.range_dim.index_of(-10)
        with self.assertRaises(IndexError):
            self.range_dim.index_of(12398, nix.IndexMode.GreaterOrEqual)
        with self.assertRaises(IndexError):
            self.range_dim.index_of(test_range[-1]+0.001, nix.IndexMode.GreaterOrEqual)


class TestLinkDimension(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("linkdimtest")
        self.testfilename = os.path.join(self.tmpdir.path, "linkdimtest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "test.session")
        self.array = self.block.create_data_array(
            "test array", "signal", nix.DataType.Float,
            data=np.random.random_sample((3, 15))
        )

        self.set_dim = self.array.append_set_dimension()
        self.range_dim = self.array.append_range_dimension()

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_data_array_range_link_dimension(self):
        tickarray = self.block.create_data_array(
            "ticks", "array.dimension.ticks",
            data=np.linspace(0, 100, 15)
        )
        tickarray.label = "DIMENSION LABEL"
        tickarray.unit = "mV"
        self.range_dim.link_data_array(tickarray, [-1])
        assert np.all(tickarray[:] == self.range_dim.ticks)
        assert tickarray.unit == self.range_dim.unit
        assert tickarray.label == self.range_dim.label

        tickarray3d = self.block.create_data_array(
            "ticks3d", "array.dimension.ticks",
            data=np.random.random_sample((20, 15, 4))
        )
        tickarray3d.unit = "mA"
        ticks = np.cumsum(np.random.random_sample(15))
        tickarray3d[3, :, 1] = ticks
        tickarray3d.label = "DIMENSION LABEL 2"
        self.range_dim.link_data_array(tickarray3d, [3, -1, 1])
        assert np.shape(ticks) == np.shape(self.range_dim.ticks)
        assert np.all(ticks == self.range_dim.ticks)
        assert tickarray3d.unit == self.range_dim.unit
        assert tickarray3d.label == self.range_dim.label

    def test_data_array_set_link_dimension(self):
        labelarray = self.block.create_data_array(
            "labels", "array.dimension.labels",
            data=["Alpha", "Beta", "Gamma"], dtype=nix.DataType.String
        )
        self.set_dim.link_data_array(labelarray, [-1])
        assert np.all(labelarray[:] == self.set_dim.labels)

        labelarray2d = self.block.create_data_array(
            "labels2d", "array.dimension.labels",
            dtype=nix.DataType.String,
            data=[["Alpha1", "Beta1", "Gamma1"],
                  ["Alpha2", "Beta2", "Gamma2"]],
        )
        self.set_dim.link_data_array(labelarray2d, [1, -1])
        assert np.all(("Alpha2", "Beta2", "Gamma2") == self.set_dim.labels)
        assert np.all(labelarray2d[1, :] == self.set_dim.labels)

    def test_data_array_self_link_range_dimension(self):
        # The new way of making alias range dimension
        da = self.block.create_data_array("alias da", "dimticks",
                                          data=np.random.random_sample(10))
        da.label = "alias dimension label"
        da.unit = "F"
        rdim = da.append_range_dimension()
        rdim.link_data_array(da, [-1])
        assert len(da.dimensions) == 1
        assert da.dimensions[0].label == da.label
        assert da.dimensions[0].unit == da.unit
        assert np.all(da.dimensions[0].ticks == da[:])
        assert rdim.is_alias

        da.delete_dimensions()
        da.append_range_dimension()
        assert not da.dimensions[0].is_alias
        
        da.delete_dimensions()
        da.append_range_dimension_using_self()
        assert len(da.dimensions) == 1
        assert da.dimensions[0].is_alias

        da.delete_dimensions()
        with self.assertRaises(IncompatibleDimensions):
            da.append_range_dimension_using_self([0, -1])
        with self.assertRaises(ValueError):
            da.append_range_dimension_using_self([-2])

        da.append_range_dimension_using_self([-1])
        assert len(da.dimensions) == 1
        assert da.dimensions[0].is_alias

    def test_data_array_self_link_set_dimension(self):
        # The new way of making alias range dimension
        labelda = self.block.create_data_array("alias da", "dimlabels",
                                               data=np.random.random_sample(10))
        rdim = labelda.append_set_dimension()
        rdim.link_data_array(labelda, [-1])
        assert len(labelda.dimensions) == 1
        assert np.all(labelda.dimensions[0].labels == labelda[:])

    def test_data_frame_range_link_dimension(self):
        column_descriptions = OrderedDict([("name", nix.DataType.String),
                                           ("id", nix.DataType.String),
                                           ("duration", nix.DataType.Double)])

        def randtick():
            time_stamp = 0
            while True:
                time_stamp += np.random.random_sample()
                yield time_stamp

        tickgen = randtick()

        values = [("Alpha", "a", next(tickgen)),
                  ("Beta", 'b',  next(tickgen)),
                  ("Gamma", 'c', next(tickgen)),
                  ("Alpha", "a", next(tickgen)),
                  ("Gamma", 'c', next(tickgen)),
                  ("Alpha", "a", next(tickgen)),
                  ("Gamma", 'c', next(tickgen)),
                  ("Alpha", "a", next(tickgen)),
                  ("Beta", 'b',  next(tickgen))]
        units = (None, None, "s")
        df = self.block.create_data_frame("df-dimension",
                                          "array.dimension.labels",
                                          col_dict=column_descriptions,
                                          data=values)
        df.units = units

        self.range_dim.link_data_frame(df, 2)
        np.testing.assert_almost_equal(self.range_dim.ticks,
                                       tuple(v[2] for v in values))
        assert self.range_dim.unit == df.units[2]
        assert self.range_dim.label == df.column_names[2]
        assert not self.range_dim.is_alias

    def test_data_frame_set_link_dimension(self):
        column_descriptions = OrderedDict([("name", nix.DataType.String),
                                           ("id", nix.DataType.String),
                                           ("duration", nix.DataType.Float)])

        def rdura():
            return np.random.random_sample() * 30

        values = [("Alpha", "a", rdura()),
                  ("Beta", 'b',  rdura()),
                  ("Gamma", 'c', rdura()),
                  ("Alpha", "a", rdura()),
                  ("Gamma", 'c', rdura()),
                  ("Alpha", "a", rdura()),
                  ("Gamma", 'c', rdura()),
                  ("Alpha", "a", rdura()),
                  ("Beta", 'b',  rdura())]
        units = (None, None, "s")
        df = self.block.create_data_frame("df-dimension",
                                          "array.dimension.labels",
                                          col_dict=column_descriptions,
                                          data=values)
        df.units = units

        self.set_dim.link_data_frame(df, 1)
        assert self.set_dim.labels == tuple(v[1] for v in values)

    def test_data_array_linking_errors(self):
        da = self.block.create_data_array("baddim", "dimension.error.test",
                                          data=np.random.random_sample((3, 4, 2)))

        # index dimensionality mismatch
        with self.assertRaises(nix.exceptions.IncompatibleDimensions):
            self.set_dim.link_data_array(da, [0, -1])
        with self.assertRaises(nix.exceptions.IncompatibleDimensions):
            self.range_dim.link_data_array(da, [0, -1, 3, 3])

        # no -1 in index
        with self.assertRaises(ValueError):
            self.set_dim.link_data_array(da, [0, 0, 0])
        with self.assertRaises(ValueError):
            self.range_dim.link_data_array(da, [1, 1, 1])

        # multiple -1  (or negative)in index
        with self.assertRaises(ValueError):
            self.set_dim.link_data_array(da, [-1, -1, 0])
        with self.assertRaises(ValueError):
            self.range_dim.link_data_array(da, [-1, -1, 1])
        with self.assertRaises(ValueError):
            self.set_dim.link_data_array(da, [-2, 0, 0])
        with self.assertRaises(ValueError):
            self.range_dim.link_data_array(da, [-2, 0, 1])
        with self.assertRaises(ValueError):
            self.set_dim.link_data_array(da, [-10, -10, 0])
        with self.assertRaises(ValueError):
            self.range_dim.link_data_array(da, [-10, -10, 1])

    def test_data_frame_linking_errors(self):
        column_descriptions = OrderedDict([("name", nix.DataType.String),
                                           ("id", nix.DataType.String),
                                           ("score", nix.DataType.Float)])
        values = [("Alpha", "a", 0),
                  ("Beta", 'b',  100),
                  ("Gamma", 'c', 50),
                  ("Alpha", "a", 10),
                  ("Gamma", 'c', 42),
                  ("Alpha", "a", 93),
                  ("Gamma", 'c', 23),
                  ("Alpha", "a", 37),
                  ("Beta", 'b',  87)]
        df = self.block.create_data_frame("df-dimension",
                                          "array.dimension.labels",
                                          col_dict=column_descriptions,
                                          data=values)
        for badidx in [-110, -5, -1, 3, 4, 34]:
            with self.assertRaises(nix.exceptions.OutOfBounds):
                self.set_dim.link_data_frame(df, badidx)
            with self.assertRaises(nix.exceptions.OutOfBounds):
                self.range_dim.link_data_frame(df, badidx)

    def test_sampled_dimension_unsupported(self):
        sdim = self.array.append_sampled_dimension(0.1)

        da = self.block.create_data_array("baddim", "dimension.error.test",
                                          data=np.random.random_sample((3, 4, 2)))
        with self.assertRaises(RuntimeError):
            sdim.link_data_array(da, [0])

        column_descriptions = OrderedDict([("name", nix.DataType.String),
                                           ("id", nix.DataType.String),
                                           ("duration", nix.DataType.Float)])
        values = [("Alpha", "a", 0),
                  ("Beta", 'b',  0),
                  ("Gamma", 'c', 0),
                  ("Alpha", "a", 0),
                  ("Gamma", 'c', 0),
                  ("Alpha", "a", 0),
                  ("Gamma", 'c', 0),
                  ("Alpha", "a", 0),
                  ("Beta", 'b',  0)]
        df = self.block.create_data_frame("df-dimension",
                                          "array.dimension.labels",
                                          col_dict=column_descriptions,
                                          data=values)

        with self.assertRaises(RuntimeError):
            sdim.link_data_array(df, 10)

    def test_write_linked_array_props(self):
        tickarray = self.block.create_data_array(
            "ticks3d", "array.dimension.ticks",
            data=np.random.random_sample((10, 5, 4))
        )
        tickarray.unit = "whatever"
        ticks = np.cumsum(np.random.random_sample(5))
        tickarray[3, :, 1] = ticks
        tickarray.label = "DIMENSION LABEL"
        self.range_dim.link_data_array(tickarray, [3, -1, 1])
        assert tickarray.unit == self.range_dim.unit
        assert tickarray.label == self.range_dim.label

        self.range_dim.unit = "something else"
        assert tickarray.unit == "something else"
        assert tickarray.unit == self.range_dim.unit

        self.range_dim.label = "MODIFIED DIMENSION LABEL"
        assert tickarray.label == "MODIFIED DIMENSION LABEL"
        assert tickarray.unit == self.range_dim.unit

    def test_write_linked_dataframe_props(self):
        column_descriptions = OrderedDict([("name", nix.DataType.String),
                                           ("id", nix.DataType.String),
                                           ("duration", nix.DataType.Double)])

        values = [("Alpha", "a", 0),
                  ("Beta", 'b',  0),
                  ("Gamma", 'c', 0),
                  ("Alpha", "a", 0),
                  ("Gamma", 'c', 0),
                  ("Alpha", "a", 0),
                  ("Gamma", 'c', 0),
                  ("Alpha", "a", 0),
                  ("Beta", 'b',  0)]
        units = (None, None, "s")
        df = self.block.create_data_frame("df-dimension",
                                          "array.dimension.labels",
                                          col_dict=column_descriptions,
                                          data=values)
        df.units = units

        self.range_dim.link_data_frame(df, 2)
        assert self.range_dim.unit == df.units[2]
        assert self.range_dim.label == df.column_names[2]

        self.range_dim.unit = "m"
        assert df.units[2] == "m"
        assert self.range_dim.unit == df.units[2]

        with self.assertRaises(RuntimeError):
            # Can't change label: column name
            self.range_dim.label = "a whole new label"

    def test_range_link_tick_replacement(self):
        tickarray = self.block.create_data_array(
            "ticks", "array.dimension.ticks",
            data=np.linspace(0, 100, 15)
        )
        assert "link" not in self.range_dim._h5group
        assert "ticks" not in self.range_dim._h5group

        # add link
        self.range_dim.link_data_array(tickarray, [-1])
        assert "link" in self.range_dim._h5group
        assert "ticks" not in self.range_dim._h5group

        # replace with ticks
        self.range_dim.ticks = np.cumsum(np.random.random_sample(10))
        assert "link" not in self.range_dim._h5group
        assert "ticks" in self.range_dim._h5group

        # replace with link again
        self.range_dim.link_data_array(tickarray, [-1])
        assert "link" in self.range_dim._h5group
        assert "ticks" not in self.range_dim._h5group
