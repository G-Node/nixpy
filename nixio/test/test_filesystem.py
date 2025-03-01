# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import pathlib
import unittest

import nixio as nix

from .tmp import TempDir


class TestFilePathlib(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("filetest")
        self.testfilename = pathlib.Path(self.tmpdir.path) / "filetest.nix"

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_with_pathlib(self):
        file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        file.close()

    def test_with_unicode(self):
        file_test = self.testfilename.parent /"👍_test.nix"
        file = nix.File.open(file_test, nix.FileMode.Overwrite)
        file.close()
