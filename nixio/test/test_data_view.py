# -*- coding: utf-8 -*-
# Copyright © 2019, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
import unittest
import numpy as np
import nixio as nix
from .tmp import TempDir


class TestDataView(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("dvtest")
        self.testfilename = os.path.join(self.tmpdir.path, "dvtest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.data = np.random.random_sample((40, 80))
        block = self.file.create_block("testblock", "nix.test.block")
        block.create_data_array("data", "nix.test.data", data=self.data)

    def tearDown(self):
        del self.file.blocks[0]
        self.file.close()
        self.tmpdir.cleanup()

    def test_data_view_read(self):
        da = self.file.blocks[0].data_arrays[0]
        dv = da.get_slice((10, 3), extents=(1, 3))
        np.testing.assert_almost_equal(dv[:], da[10:11, 3:6])

    def test_data_view_read_2d_str_array(self):
        numbers = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
        data = np.empty((10, 4), dtype=str)
        for i in range(10):
            for j in range(4):
                data[i, j] = " ".join([numbers[i], numbers[j]])
        da = self.file.blocks[0].create_data_array("str_2d_array", "test", dtype=nix.DataType.String, data=data)
        da.append_set_dimension()
        da.append_set_dimension()

        dv = da.get_slice((0, 0), extents=(10, 4))
        npeq = np.testing.assert_equal
        npeq(dv.shape, da.shape)
        npeq(dv[:], data)
        for d in dv[:]:
            assert("numpy.str_" not in str(type(d)))

    def test_data_view_fancy_slicing(self):
        da = self.file.blocks[0].data_arrays[0]
        dv = da.get_slice((5, 8), extents=(10, 20))

        npeq = np.testing.assert_almost_equal

        # when stop > length, stops at len-1
        npeq(dv[:100, 1], da[5:15, 9])
        npeq(dv[0, 5:2000], da[5, 13:28])
        npeq(dv[9:100, 18:1000], da[14:15, 26:28])

        # negative slicing
        npeq(dv[-5:, 1], da[10:15, 9])
        npeq(dv[-5:-2, -1], da[10:13, 27])
        npeq(dv[:, -10:13], da[5:15, 18:21])

    def test_data_view_write_direct(self):
        da = self.file.blocks[0].data_arrays[0]
        np.testing.assert_almost_equal(da[:], self.data)

        dv = da.get_slice((10, 3), extents=(1, 3))
        dv.write_direct([1, 2, 3])

        newdata = self.data.copy()
        newdata[10:11, 3:6] = [1, 2, 3]

        np.testing.assert_almost_equal(da[:], newdata)

    def test_data_view_write_index(self):
        """
        Write through DataView to the underlying DataArray using [slice]
        notation.

        Update copy of underlying data with expected values and compare
        directly to DataArray for assertions.
        """
        da = self.file.blocks[0].data_arrays[0]
        dv = da.get_slice((10, 20), extents=(20, 15))
        newdata = self.data.copy()

        npeq = np.testing.assert_almost_equal

        # straightforward slicing
        rand_data = np.random.random_sample((3, 4))
        dv[0:3, 1:5] = rand_data
        newdata[10:13, 21:25] = rand_data
        npeq(da[:], newdata)

        # slicing with steps
        rand_data = np.random.random_sample((5, 3))
        dv[0:20:4, 0:15:5] = rand_data
        newdata[10:30:4, 20:35:5] = rand_data
        npeq(da[:], newdata)

        # steps only
        rand_data = np.random.random_sample((5, 3))
        dv[::4, ::5] = rand_data
        newdata[10:30:4, 20:35:5] = rand_data
        npeq(da[:], newdata)

        # plain index
        dv[1, 1] = 20
        newdata[11, 21] = 20
        npeq(da[:], newdata)

        # negative index
        dv[-1, -1] = 80
        newdata[29, 34] = 80
        npeq(da[:], newdata)

        # negative slice start
        rand_data = np.random.random_sample(3)
        dv[-3::, 10] = rand_data
        newdata[27:30, 30] = rand_data
        npeq(da[:], newdata)

        # negative slice stop
        rand_data = np.random.random_sample(15)
        dv[:-5, 2] = rand_data
        newdata[10:25, 22] = rand_data
        npeq(da[:], newdata)

        # negative slice start and stop
        rand_data = np.random.random_sample(10)
        dv[10, -15:-5] = rand_data
        newdata[20, 20:30] = rand_data
        npeq(da[:], newdata)

    def test_data_view_oob(self):
        da = self.file.blocks[0].data_arrays[0]

        dv = da.get_slice((41, 81), extents=(1, 1))
        assert not dv.valid
        assert "OutOfBounds error" in dv.debug_message

        dv = da.get_slice((0, 0), extents=(100, 5))
        assert not dv.valid
        assert "OutOfBounds error" in dv.debug_message

        with self.assertRaises(nix.exceptions.IncompatibleDimensions):
            da.get_slice((0, 0, 0), extents=(5, 5, 5))

        dv = da.get_slice((5, 8), extents=(10, 20))
        assert dv.valid

        with self.assertRaises(nix.exceptions.OutOfBounds):
            _ = dv[12, :]

        with self.assertRaises(nix.exceptions.OutOfBounds):
            _ = dv[12, :]

        with self.assertRaises(nix.exceptions.OutOfBounds):
            _ = dv[10]

        with self.assertRaises(nix.exceptions.OutOfBounds):
            _ = dv[0, 20]

        with self.assertRaises(nix.exceptions.OutOfBounds):
            _ = dv[:, 25]

        with self.assertRaises(nix.exceptions.OutOfBounds):
            _ = dv[-11]

        with self.assertRaises(nix.exceptions.OutOfBounds):
            _ = dv[0, -21]

    def test_data_view_ellipsis(self):
        block = self.file.blocks[0]
        data = np.random.random_sample((10, 11, 12, 13, 14))
        da = block.create_data_array("data2", "nix.test.data", data=data)

        npeq = np.testing.assert_almost_equal

        dv = da.get_slice((5, 6, 7, 8, 9), (5, 5, 5, 5, 5))
        npeq(dv[1, ..., 2], da[6, 6:11, 7:12, 8:13, 11])
        npeq(dv[..., 0, 0], da[5:10, 6:11, 7:12, 8, 9])
        npeq(dv[1:3, 0, ...], da[6:8, 6, 7:12, 8:13, 9:14])
        npeq(dv[1:3, :, ...], da[6:8, 6:11, 7:12, 8:13, 9:14])
