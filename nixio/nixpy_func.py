from __future__ import (absolute_import, division, print_function)
import os
import shutil
import unittest
import h5py
import numpy as np
import nixio as nix
import nixio.pycore.file as filepy
from nixio.pycore.exceptions.exceptions import InvalidFile
from nixio.pycore.file import File
from nixio.test.test_file import FileTestBase



# class Test(FileTestBase, unittest.TestCase):
#     unittest.main()

file = nix.File.open("/home/choi/PycharmProjects/nixpy/nixio/pycore/neoraw.nix")
file.validate()


