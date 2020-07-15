# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
import unittest
import numpy as np

import nixio as nix
from .tmp import TempDir
from collections import OrderedDict


test_range = tuple([float(i) for i in range(10)])
test_sampl = 0.1
test_label = "test label"
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
        self.sample_dim = self.array.append_sampled_dimension(test_sampl)
        self.range_dim = self.array.append_range_dimension(test_range)

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_set_dimension(self):
        assert(self.set_dim.index == 1)
        assert(self.set_dim.dimension_type == nix.DimensionType.Set)
        assert(self.array.dimensions[0].index == 1)

        assert(self.set_dim.labels == ())
        self.set_dim.labels = test_labels
        assert(self.set_dim.labels == test_labels)

    def test_sample_dimension(self):
        assert(self.sample_dim.index == 2)
        assert(self.sample_dim.dimension_type == nix.DimensionType.Sample)
        assert(self.array.dimensions[1].index == 2)

        assert(self.sample_dim.label is None)
        self.sample_dim.label = test_label
        assert(self.sample_dim.label == test_label)
        self.sample_dim.label = None
        assert(self.sample_dim.label is None)

        assert(self.sample_dim.unit is None)
        self.sample_dim.unit = "mV"
        assert(self.sample_dim.unit == "mV")
        self.sample_dim.unit = None
        assert(self.sample_dim.unit is None)

        assert(self.sample_dim.sampling_interval == test_sampl)
        self.sample_dim.sampling_interval = 1.123
        assert(self.sample_dim.sampling_interval == 1.123)

        assert(self.sample_dim.offset is None)
        self.sample_dim.offset = 0.3
        assert(self.sample_dim.offset == 0.3)
        self.sample_dim.offset = None
        assert(self.sample_dim.offset is None)

        self.sample_dim.sampling_interval = 2.
        self.sample_dim.offset = 3.

        assert(self.sample_dim.index_of(3.14) == 0)
        assert(self.sample_dim.index_of(23.) == 10)
        assert(type(self.sample_dim.index_of(23.) == int))

        assert(self.sample_dim.position_at(0) == 3.)
        assert(self.sample_dim.position_at(200) == 200*2.+3.)

        assert(len(self.sample_dim.axis(10)) == 10)
        assert(self.sample_dim.axis(10)[0] == 3.)
        assert(self.sample_dim.axis(10)[-1] == 9*2.+3.)

        assert(len(self.sample_dim.axis(10, 2)) == 10)
        assert(self.sample_dim.axis(10, 2)[0] == 2 * 2. + 3.)
        assert(self.sample_dim.axis(10, 2)[-1] == (9 + 2) * 2. + 3.)

    def test_range_dimension(self):
        assert(self.range_dim.index == 3)
        assert(self.range_dim.dimension_type == nix.DimensionType.Range)
        assert(self.array.dimensions[2].index == 3)

        assert(self.range_dim.label is None)
        self.range_dim.label = test_label
        assert(self.range_dim.label == test_label)
        self.range_dim.label = None
        assert(self.range_dim.label is None)

        assert(self.range_dim.unit is None)
        self.range_dim.unit = "mV"
        assert(self.range_dim.unit == "mV")
        self.range_dim.unit = None
        assert(self.range_dim.unit is None)

        assert(self.range_dim.ticks == test_range)
        other = tuple([i*3.14 for i in range(10)])
        self.range_dim.ticks = other
        assert(self.range_dim.ticks == other)

        assert(self.range_dim.index_of(0.) == 0)
        assert(self.range_dim.index_of(10.) == (np.floor(10./3.14)))
        assert(self.range_dim.index_of(18.84) == 6)
        assert(self.range_dim.index_of(28.26) == 9)
        assert(self.range_dim.index_of(100.) == 9)
        assert(self.range_dim.index_of(-100.) == 0)

        assert(self.range_dim.tick_at(0) == 0)
        assert(self.range_dim.tick_at(9) == other[-1])
        with self.assertRaises(IndexError):
            self.range_dim.tick_at(100)

        assert(self.range_dim.axis(10) == other)
        assert(self.range_dim.axis(2) == other[:2])
        assert(self.range_dim.axis(2, 2) == other[2:4])
        with self.assertRaises(IndexError):
            self.range_dim.axis(10, 2)
            self.range_dim.axis(100)

    def test_set_dim_label_resize(self):
        setdim = self.array.append_set_dimension()
        labels = ["A", "B"]
        setdim.labels = labels
        assert tuple(labels) == setdim.labels

        newlabels = ["C", "B", "A"]
        setdim.labels = newlabels
        assert tuple(newlabels) == setdim.labels

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


class TestLinkDimension(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("linkdimtest")
        self.testfilename = os.path.join(self.tmpdir.path, "linkdimtest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "test.session")
        self.array = self.block.create_data_array(
            "test array", "signal", nix.DataType.Float,
            data=np.random.random((3, 15))
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
        assert np.all(tickarray.unit == self.range_dim.unit)
        assert np.all(tickarray.label == self.range_dim.label)

        tickarray3d = self.block.create_data_array(
            "ticks3d", "array.dimension.ticks",
            data=np.random.random((20, 15, 4))
        )
        tickarray3d.unit = "mA"
        ticks = np.cumsum(np.random.random(15))
        tickarray3d[3, :, 1] = ticks
        tickarray3d.label = "DIMENSION LABEL 2"
        self.range_dim.link_data_array(tickarray3d, [3, -1, 1])
        assert np.shape(ticks) == np.shape(self.range_dim.ticks)
        assert np.all(ticks == self.range_dim.ticks)
        assert np.all(tickarray3d.unit == self.range_dim.unit)
        assert np.all(tickarray3d.label == self.range_dim.label)

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
                                          data=np.random.random(10))
        da.label = "alias dimension label"
        da.unit = "F"
        rdim = da.append_range_dimension()
        rdim.link_data_array(da, [-1])
        assert len(da.dimensions) == 1
        assert da.dimensions[0].label == da.label
        assert da.dimensions[0].unit == da.unit
        assert np.all(da.dimensions[0].ticks == da[:])

    def test_data_array_self_link_set_dimension(self):
        # The new way of making alias range dimension
        labelda = self.block.create_data_array("alias da", "dimlabels",
                                               data=np.random.random(10))
        rdim = labelda.append_set_dimension()
        rdim.link_data_array(labelda, [-1])
        assert len(labelda.dimensions) == 1
        assert np.all(labelda.dimensions[0].labels == labelda[:])

    def test_data_frame_range_link_dimension(self):
        column_descriptions = OrderedDict([("name", nix.DataType.String),
                                           ("id", nix.DataType.String),
                                           ("duration", nix.DataType.Double)])

        def randtick():
            ts = 0
            while True:
                ts += np.random.random()
                yield ts

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

    def test_data_frame_set_link_dimension(self):
        column_descriptions = OrderedDict([("name", nix.DataType.String),
                                           ("id", nix.DataType.String),
                                           ("duration", nix.DataType.Float)])

        def rdura():
            return np.random.random() * 30

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

    def test_linking_errors(self):
        pass
