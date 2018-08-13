from __future__ import (absolute_import, division, print_function)
import nixio as nix
import numpy as np
import os
import unittest
from .tmp import TempDir


class TestValidate (unittest.TestCase):

    def Setup(self):
        self.tmpdir = TempDir("blocktest")
        self.testfilename = os.path.join(self.tmpdir.path, "blocktest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.other = self.file.create_block("other block", "recordingsession")