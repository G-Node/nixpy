# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)
import os

import unittest

import nixio as nix


class TestFeatures(unittest.TestCase):

    testfilename = "featuretest.h5"

    def setUp(self):
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")

        self.signal = self.block.create_data_array("output", "analogsignal",
                                                   nix.DataType.Float, (0, ))
        self.stimuli_tag = self.block.create_tag(
            "stimuli used", "tag", [0]
        )
        self.stimuli_tag.references.append(self.signal)

        self.movie1 = self.block.create_data_array("stimulus movie 1", "movie",
                                                   nix.DataType.Float, (0, ))
        self.feature_1 = self.stimuli_tag.create_feature(
            self.movie1, nix.LinkType.Tagged
        )
        self.movie2 = self.block.create_data_array("stimulus movie 2", "movie",
                                                   nix.DataType.Float, (0, ))
        self.feature_2 = self.stimuli_tag.create_feature(
            self.movie2, nix.LinkType.Tagged
        )

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        os.remove(self.testfilename)

    def test_feature_eq(self):
        assert(self.feature_1 == self.feature_1)
        assert(not self.feature_1 == self.feature_2)
        assert(self.feature_1 is not None)

    def test_feature_id(self):
        assert(self.feature_1.id is not None)

    def test_feature_link_type(self):
        def set_none():
            self.feature_1.link_type = None

        assert(self.feature_1.link_type is not None)
        self.assertRaises(Exception, set_none)

        self.feature_1.link_type = nix.LinkType.Untagged
        assert(self.feature_1.link_type == nix.LinkType.Untagged)

    def test_feature_data(self):
        def set_none():
            self.feature_1.data = None

        assert(self.feature_1.data is not None)
        self.assertRaises(Exception, set_none)

        new_data_ref = self.block.create_data_array("test", "current",
                                                    nix.DataType.Float, (0, ))
        self.feature_1.data = new_data_ref
        assert(self.feature_1.data == new_data_ref)
