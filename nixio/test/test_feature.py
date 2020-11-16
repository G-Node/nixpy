# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
import time
import unittest
from collections import OrderedDict
import nixio as nix
from .tmp import TempDir


class TestFeatures(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("featuretest")
        self.testfilename = os.path.join(self.tmpdir.path, "featuretest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")

        self.group = self.block.create_group("test group", "feature test")

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
        self.tmpdir.cleanup()

    def test_feature_eq(self):
        assert self.feature_1 == self.feature_1
        assert not self.feature_1 == self.feature_2
        assert self.feature_1 is not None

    def test_feature_id(self):
        assert self.feature_1.id is not None

    def test_feature_link_type(self):
        def set_none():
            self.feature_1.link_type = None

        assert self.feature_1.link_type is not None
        self.assertRaises(Exception, set_none)

        self.feature_1.link_type = nix.LinkType.Untagged
        assert self.feature_1.link_type == nix.LinkType.Untagged

    def test_feature_data(self):
        def set_none():
            self.feature_1.data = None

        assert self.feature_1.data is not None
        self.assertRaises(Exception, set_none)

        new_data_ref = self.block.create_data_array("test", "current",
                                                    nix.DataType.Float, (0, ))
        self.feature_1.data = new_data_ref
        assert self.feature_1.data == new_data_ref

    def test_feature_dataframe(self):
        coltypes = OrderedDict(
            idx=int,
            name=str,
            value=float,
        )
        new_data_frame = self.block.create_data_frame("table", "test.feature",
                                                      col_dict=coltypes)
        df_feature = self.stimuli_tag.create_feature(new_data_frame, nix.LinkType.Indexed)
        assert df_feature.data == new_data_frame

    def test_feature_on_group(self):
        grouptag = self.block.create_tag("I am tag", "grouptest", [0])
        self.group.tags.append(grouptag)

        grouptag = self.group.tags[-1]
        grouptag.create_feature(self.movie1, nix.LinkType.Tagged)

    def test_create_diff_link_type_style(self):
        self.stimuli_tag.create_feature(self.movie1, nix.LinkType.Tagged)

    def test_timestamp_autoupdate(self):
        array = self.block.create_data_array("array.time", "signal",
                                             nix.DataType.Double, (100, ))
        feature = self.stimuli_tag.create_feature(array, nix.LinkType.Tagged)

        ftime = feature.updated_at
        time.sleep(1)
        feature.data = self.block.create_data_array("alt.array", "signal",
                                                    nix.DataType.Int8, (1,))
        self.assertNotEqual(ftime, feature.updated_at)

        ftime = feature.updated_at
        time.sleep(1)
        feature.link_type = nix.LinkType.Untagged
        self.assertNotEqual(ftime, feature.updated_at)

    def test_timestamp_noautoupdate(self):
        self.file.auto_update_timestamps = False
        array = self.block.create_data_array("array.time", "signal",
                                             nix.DataType.Double, (100, ))
        feature = self.stimuli_tag.create_feature(array, nix.LinkType.Tagged)

        ftime = feature.updated_at
        time.sleep(1)
        feature.data = self.block.create_data_array("alt.array", "signal",
                                                    nix.DataType.Int8, (1,))
        self.assertEqual(ftime, feature.updated_at)

        ftime = feature.updated_at
        time.sleep(1)
        feature.link_type = nix.LinkType.Untagged
        self.assertEqual(ftime, feature.updated_at)
