# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

import unittest

from nixio import *
try:
    import nixio.core
    skip = False
except ImportError:
    skip = True


@unittest.skipIf(skip, "HDF5 backend not available.")
class TestCompatibility(unittest.TestCase):

    pass
