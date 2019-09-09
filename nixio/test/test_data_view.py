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
        self.data = np.zeros((20, 30))
        block = self.file.create_block("testblock", "nix.test.block")
        block.create_data_array("data", "nix.test.data", data=self.data)

    def tearDown(self):
        del self.file.blocks[0]
        self.file.close()
        self.tmpdir.cleanup()

    def test_data_view_write(self):
        da = self.file.blocks[0].data_arrays[0]
        np.testing.assert_almost_equal(da[:], self.data)

        dv = da.get_slice((10, 3), extents=(1, 3))
        dv.write_direct([1, 2, 3])

        newdata = self.data.copy()
        newdata[10:11, 3:6] = [1, 2, 3]

        np.testing.assert_almost_equal(da[:], newdata)
