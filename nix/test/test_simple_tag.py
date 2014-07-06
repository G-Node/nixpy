# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from nix import *


class TestProperty(unittest.TestCase):

    def setUp(self):
        self.file     = File.open("unittest.h5", FileMode.Overwrite)
        self.block    = self.file.create_block("test block", "recordingsession")
        self.my_tag   = self.block.create_simple_tag("test array", "signal")
        self.your_tag = self.block.create_simple_tag("other array", "signal")

    def tearDown(self):
        del self.file.sections[self.section.id]
        self.file.close()

