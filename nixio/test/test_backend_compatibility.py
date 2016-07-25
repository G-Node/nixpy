# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

import unittest
import numpy as np

from nixio import *
try:
    import nixio.core
    skip = False
except ImportError:
    skip = True


all_attrs = [
    "id", "created_at", "updated_at", "name", "type", "definition",
    "dtype", "polynom_coefficients", "expansion_origin", "label", "labels",
    "unit", "data_extent", "data_type", "dimension_type", "index",
    "sampling_interval", "offset", "ticks", "metadata", "link_type", "data",
    "positions", "extents", "mapping", "values", "parent", "link",
    "repository", "units", "position", "extent"
]


@unittest.skipIf(skip, "HDF5 backend not available.")
class _TestBackendCompatibility(unittest.TestCase):

    def setUp(self):
        self.write_file = File.open("compat_test.h5", FileMode.Overwrite,
                                    backend=self.write_backend)
        self.read_file = None

    def tearDown(self):
        self.write_file.close()
        if self.read_file:
            self.read_file.close()

    def check_attributes(self, writeitem, readitem):
        for attr in all_attrs:
            if hasattr(writeitem, attr) or hasattr(readitem, attr):
                writeval = getattr(writeitem, attr)
                readval = getattr(readitem, attr)
                self.assertEqual(
                    writeval, readval,
                    "Attribute mismatch between {} and {} "
                    "for attribute '{}': {} != {}".format(
                        writeitem, readitem, attr, writeval, readval
                    ))

    def check_recurse(self, writecont, readcont):
        self.assertEqual(len(writecont), len(readcont))
        for idx in range(len(writecont)):
            writeitem = writecont[idx]
            readitem = readcont[idx]
            self.check_attributes(writeitem, readitem)
            if len(writeitem.sources) or len(readitem.sources):
                self.check_recurse(writeitem.sources, readitem.sources)

    def check_compatibility(self):
        self.read_file = File.open("compat_test.h5", FileMode.ReadOnly,
                                   backend=self.read_backend)

        self.check_recurse(self.write_file.blocks, self.read_file.blocks)

        for blkidx in range(len(self.write_file.blocks)):
            wblock = self.write_file.blocks[blkidx]
            rblock = self.read_file.blocks[blkidx]
            self.check_recurse(wblock.groups, rblock.groups)
            self.check_recurse(wblock.data_arrays, rblock.data_arrays)
            self.check_recurse(wblock.tags, rblock.tags)
            self.check_recurse(wblock.multi_tags, rblock.multi_tags)
            for grpidx in range(len(wblock.groups)):
                wgrp = wblock.groups[grpidx]
                rgrp = rblock.groups[grpidx]
                self.check_recurse(wgrp.data_arrays, rgrp.data_arrays)
                self.check_recurse(wgrp.tags, rgrp.tags)
                self.check_recurse(wgrp.multi_tags, rgrp.multi_tags)

    def test_blocks(self):
        for idx in range(10):
            blk = self.write_file.create_block("test_block" + str(idx),
                                               "blocktype")
            blk.definition = "definition block " + str(idx)
            blk.force_created_at(np.random.randint(100000000))

        self.check_compatibility()

    def test_groups(self):
        blk = self.write_file.create_block("test_block", "blocktype")
        for idx in range(12):
            grp = blk.create_group("group_" + str(idx), "grouptype")
            grp.definition = "group definition " + str(idx*10)
            grp.force_created_at(np.random.randint(100000000))

        self.check_compatibility()

    def test_data_arrays(self):
        blk = self.write_file.create_block("testblock", "blocktype")
        grp = blk.create_group("testgroup", "grouptype")

        for idx in range(7):
            da = blk.create_data_array("data_" + str(idx), "thedata",
                                       data=np.random.random(40))
            da.definition = "da definition " + str(sum(da[:]))
            da.force_created_at(np.random.randint(100000000))
            da.label = "data label " + str(idx)
            da.unit = "mV"

            if (idx % 2) == 0:
                da.expansion_origin = np.random.random()*100
                grp.data_arrays.append(da)
            if (idx % 3) == 0:
                da.polynom_coefficients = tuple(np.random.random(3))

        self.check_compatibility()
        wdata = blk.data_arrays
        rdata = self.read_file.blocks[0].data_arrays
        self.assertEqual(len(wdata), len(rdata))
        for wda, rda in zip(wdata, rdata):
            warray = np.empty(wda.shape)
            wda.read_direct(warray)
            rarray = np.empty(rda.shape)
            rda.read_direct(rarray)
            np.testing.assert_almost_equal(
                warray, rarray,
                err_msg="DataArray direct data mismatch "
                        "while testing {}".format(wda.name)
            )
            np.testing.assert_almost_equal(
                wda[:], rda[:],
                err_msg="DataArray data mismatch "
                        "while testing {}".format(wda.name)
            )
            start = np.random.randint(40)
            end = start + np.random.randint(40-start)
            np.testing.assert_almost_equal(
                wda[start:end], rda[start:end],
                err_msg="DataArray partial data mismatch "
                        "while testing {}".format(wda.name)
            )

    def test_tags(self):
        blk = self.write_file.create_block("testblock", "blocktype")
        grp = blk.create_group("testgroup", "grouptype")

        for idx in range(16):
            tag = blk.create_tag("tag_" + str(idx), "atag",
                                 np.random.random(idx*2))
            tag.definition = "tag def " + str(idx)
            tag.extent = np.random.random(idx*2)

            tag.units = ["mV", "s"]
            tag.force_created_at(np.random.randint(100000000))

            if (idx % 3) == 0:
                grp.tags.append(tag)

        self.check_compatibility()
        wtags = blk.tags
        rtags = self.read_file.blocks[0].tags
        for wtag, rtag in zip(rtags, wtags):
            np.testing.assert_almost_equal(wtag.position, rtag.position)
            np.testing.assert_almost_equal(wtag.extent, rtag.extent)

    def test_multi_tags(self):
        blk = self.write_file.create_block("testblock", "blocktype")
        grp = blk.create_group("testgroup", "grouptype")

        for idx in range(11):
            posda = blk.create_data_array("pos_" + str(idx), "positions",
                                          data=np.random.random(idx*10))
            extda = blk.create_data_array("ext_" + str(idx), "extents",
                                          data=np.random.random(idx*10))
            mtag = blk.create_multi_tag("mtag_" + str(idx), "some multi tag",
                                        posda)
            mtag.extents = extda

            if (idx % 2) == 0:
                grp.multi_tags.append(mtag)

        self.check_compatibility()
        wmts = blk.multi_tags
        rmts = self.read_file.blocks[0].multi_tags
        for wmt, rmt in zip(wmts, rmts):
            np.testing.assert_almost_equal(wmt.positions[:], rmt.positions[:])
            np.testing.assert_almost_equal(wmt.extents[:], rmt.extents[:])

    def test_sources(self):
        blk = self.write_file.create_block("testblock", "sourcetest")
        grp = blk.create_group("testgroup", "sourcetest")
        da = blk.create_data_array("da", "sourcetest",
                                   data=np.random.random(10))
        pos = blk.create_data_array("pos", "sourcetest",
                                    data=np.random.random(10))
        mtag = blk.create_multi_tag("mtag", "sourcetest", pos)
        grp.data_arrays.append(da)

        for idx in range(20):
            src = blk.create_source("src" + str(idx), "source")

            if (idx % 5) == 0:
                grp.sources.append(src)

            if (idx % 3) == 0:
                mtag.sources.append(src)

            if (idx % 8) == 0:
                da.sources.append(src)

        self.check_compatibility()

    def test_dimensions(self):
        blk = self.write_file.create_block("testblock", "dimtest")

        da_set = blk.create_data_array("da with seet", "datype",
                                       data=np.random.random(20))
        da_set.append_set_dimension()
        da_set.dimensions[0].labels = ["label one", "label two"]

        da_range = blk.create_data_array("da with range", "datype",
                                         data=np.random.random(12))
        rngdim = da_range.append_range_dimension(np.random.random(12))
        rngdim.label = "range dim label"
        rngdim.unit = "ms"

        da_sample = blk.create_data_array("da with sample", "datype",
                                          data=np.random.random(10))
        smpldim = da_sample.append_sampled_dimension(0.3)
        smpldim.offset = 0.1
        smpldim.unit = "mV"

        da_sample.dimensions[0].label = "sample dim label"

        da_multi_dim = blk.create_data_array("da with multiple", "datype",
                                             data=np.random.random(30))
        da_multi_dim.append_sampled_dimension(0.1)
        da_multi_dim.append_set_dimension()
        da_multi_dim.append_range_dimension(np.random.random(10))

        self.check_compatibility()

        for idx in range(len(blk.data_arrays)):
            wda = self.write_file.blocks[0].data_arrays[idx]
            rda = self.read_file.blocks[0].data_arrays[idx]
            for wdadim, rdadim in zip(wda.dimensions, rda.dimensions):
                self.check_attributes(wdadim, rdadim)

    def test_features(self):
        blk = self.write_file.create_block("testblock", "feattest")
        da_ref = blk.create_data_array("da for ref", "datype",
                                       DataType.Double,
                                       data=np.random.random(5))
        tag_feat = blk.create_tag("tag for feat", "tagtype", [2, 3])
        tag_feat.references.append(da_ref)

        for idx in range(4):
            da_feat = blk.create_data_array("da for feat " + str(idx),
                                            "datype",
                                            DataType.Float,
                                            data=np.random.random(3))
            da_feat.append_sampled_dimension(1.0)
            tag_feat.create_feature(da_feat, LinkType.Tagged)

        self.check_compatibility()

        wtag = self.write_file.blocks[0].tags[0]
        rtag = self.read_file.blocks[0].tags[0]
        for wfeat, rfeat in zip(wtag.features, rtag.features):
            self.check_attributes(wfeat, rfeat)
            self.check_attributes(wfeat.data, rfeat.data)
            np.testing.assert_almost_equal(wfeat.data[:], rfeat.data[:])

        wdata = wtag.retrieve_feature_data(0)
        rdata = rtag.retrieve_feature_data(0)
        self.check_attributes(wdata, rdata)
        print(wdata[:])
        np.testing.assert_almost_equal(wdata[:], rdata[:])

    def test_file(self):
        pass

    def test_properties(self):
        pass

    def test_sections(self):
        pass


class TestWriteCPPReadPy(_TestBackendCompatibility):

    write_backend = "hdf5"
    read_backend = "h5py"


class TestWritePyReadCPP(_TestBackendCompatibility):

    write_backend = "h5py"
    read_backend = "hdf5"
