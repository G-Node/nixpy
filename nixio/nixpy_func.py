from __future__ import (absolute_import, division, print_function)
import os
import shutil
import unittest
import h5py
import numpy as np
import nixio as nix
import nixio.file as filepy
from nixio.exceptions.exceptions import InvalidFile
from nixio.file import File
from nixio.test.test_file import TestFile



# class Test(TestFile, unittest.TestCase):
#     unittest.main()

file = nix.File.open("/home/choi/PycharmProjects/nixpy/nixio/neoraw.nix")
file.validate()


