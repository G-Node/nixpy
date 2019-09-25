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
        self.data = np.random.random((40, 80))
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

        # straightforward slicing
        ow = np.random.random((3, 4))
        dv[0:3, 1:5] = ow
        newdata[10:13, 21:25] = ow
        np.testing.assert_almost_equal(da[:], newdata)

        # slicing with steps
        ow = np.random.random((5, 3))
        dv[0:20:4, 0:15:5] = ow
        newdata[10:30:4, 20:35:5] = ow
        np.testing.assert_almost_equal(da[:], newdata)

        # steps only
        ow = np.random.random((5, 3))
        dv[::4, ::5] = ow
        newdata[10:30:4, 20:35:5] = ow
        np.testing.assert_almost_equal(da[:], newdata)

        # plain index
        dv[1, 1] = 20
        newdata[11, 21] = 20
        np.testing.assert_almost_equal(da[:], newdata)

        # negative index
        dv[-1, -1] = 80
        newdata[29, 34] = 80
        np.testing.assert_almost_equal(da[:], newdata)

        # negative slice start
        ow = np.random.random(3)
        dv[-3::, 10] = ow
        newdata[27:30, 30] = ow
        np.testing.assert_almost_equal(da[:], newdata)

        # negative slice stop
        ow = np.random.random(15)
        dv[:-5, 2] = ow
        newdata[10:25, 22] = ow
        np.testing.assert_almost_equal(da[:], newdata)

        # negative slice start and stop
        ow = np.random.random(10)
        dv[10, -15:-5] = ow
        newdata[20, 20:30] = ow
        np.testing.assert_almost_equal(da[:], newdata)

    def test_data_view_oob_write(self):
        pass

    def test_data_view_oob_read(self):
        pass
