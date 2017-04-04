# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)

import unittest
import numpy as np
import nixio as nix
try:
    nix.core
    skip_cpp = False
except AttributeError:
    skip_cpp = True

test_range = tuple([float(i) for i in range(10)])
test_sampl = 0.1
test_label = "test label"
test_labels = tuple([str(i) + "_label" for i in range(10)])


class _TestDimensions(unittest.TestCase):

    backend = None

    def setUp(self):
        self.file = nix.File.open("unittest.h5", nix.FileMode.Overwrite,
                                  backend=self.backend)
        self.block = self.file.create_block("test block", "recordingsession")
        self.array = self.block.create_data_array("test array", "signal",
                                                  nix.DataType.Float, (0, ))

        self.set_dim = self.array.append_set_dimension()
        self.sample_dim = self.array.append_sampled_dimension(test_sampl)
        self.range_dim = self.array.append_range_dimension(test_range)

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()

    def test_set_dimension(self):
        assert(self.set_dim.index == 1)
        assert(self.set_dim.dimension_type == nix.DimensionType.Set)

        assert(self.set_dim.labels == ())
        self.set_dim.labels = test_labels
        assert(self.set_dim.labels == test_labels)

    def test_sample_dimension(self):
        assert(self.sample_dim.index == 2)
        assert(self.sample_dim.dimension_type == nix.DimensionType.Sample)

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

        assert(self.sample_dim.position_at(0) == 3.)
        assert(self.sample_dim.position_at(200) == 200*2.+3.)

        assert(len(self.sample_dim.axis(10)) == 10)
        assert(self.sample_dim.axis(10)[0] == 3.)
        assert(self.sample_dim.axis(10)[-1] == 9*2.+3.)

    def test_range_dimension(self):
        assert(self.range_dim.index == 3)
        assert(self.range_dim.dimension_type == nix.DimensionType.Range)

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
        assert(self.range_dim.index_of(10.) == (np.ceil(10./3.14)))
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


@unittest.skipIf(skip_cpp, "HDF5 backend not available.")
class TestDimensionsCPP(_TestDimensions):

    backend = "hdf5"


class TestDimensionsPy(_TestDimensions):

    backend = "h5py"
