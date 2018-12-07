# -*- coding: utf-8 -*-
# Copyright © 2018, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
from six import string_types
from subprocess import Popen, PIPE
import numpy as np
import tempfile
import pytest

import nixio as nix
from .xcompat.compile import maketests


BINDIR = tempfile.mkdtemp(prefix="nixpy-tests-")

# skip these tests if nix isn't available
if pytest.config.getoption("--force-compat"):
    print("Forcing compatibility tests")
    maketests(BINDIR)
else:
    pytestmark = pytest.mark.skipif(
        "skip()",
        reason="Compatibility tests require the C++ NIX library")

dtypes = (
    nix.DataType.UInt8,
    nix.DataType.UInt16,
    nix.DataType.UInt32,
    nix.DataType.UInt64,
    nix.DataType.Int8,
    nix.DataType.Int16,
    nix.DataType.Int32,
    nix.DataType.Int64,
    nix.DataType.Float,
    nix.DataType.Double,
    nix.DataType.String,
    nix.DataType.Bool
)


def skip():
    return not maketests(BINDIR)


def validate(fname):
    """
    Runs the nix validation function on the given file.
    """
    runcpp("validate", fname)


def runcpp(command, *args):
    cmdbin = os.path.join(BINDIR, command)
    cmdargs = [cmdbin]
    cmdargs.extend(args)
    proc = Popen(cmdargs, stdout=PIPE, stderr=PIPE)
    proc.wait()
    stdout = proc.stdout.read().decode()
    stderr = proc.stderr.read().decode()
    # print(stdout)
    # print(stderr)
    if proc.returncode:
        raise ValueError(stdout+stderr)


def test_blocks(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "blocktest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    for idx in range(10):
        blk = nix_file.create_block("test_block" + str(idx),
                                    "blocktype")
        blk.definition = "definition block " + str(idx)
        blk.force_created_at(np.random.randint(1000000000))

    nix_file.close()
    # validate(nixfilepath)
    runcpp("readblocks", nixfilepath)


def test_groups(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "grouptest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    blk = nix_file.create_block("test_block", "blocktype")
    for idx in range(12):
        grp = blk.create_group("group_" + str(idx), "grouptype")
        grp.definition = "group definition " + str(idx*10)
        grp.force_created_at(np.random.randint(1000000000))

    nix_file.close()
    # validate(nixfilepath)
    runcpp("readgroups", nixfilepath)


def _test_data_arrays(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "arraytest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    blk = nix_file.create_block("testblock", "blocktype")
    grp = blk.create_group("testgroup", "grouptype")

    for idx in range(7):
        da = blk.create_data_array("data_" + str(idx), "thedata",
                                   data=np.random.random(40))
        da.definition = "da definition " + str(sum(da[:]))
        da.force_created_at(np.random.randint(1000000000))
        da.label = "data label " + str(idx)
        da.unit = "mV"

        if (idx % 2) == 0:
            da.expansion_origin = np.random.random()*100
            grp.data_arrays.append(da)
        if (idx % 3) == 0:
            da.polynom_coefficients = tuple(np.random.random(3))

    nix_file.close()
    # validate(nixfilepath)


def test_data_frames(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "frametest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    print(nixfilepath, nix_file)
    blk = nix_file.create_block("testblock", "blocktype")
    grp = blk.create_group("testgroup", "grouptype")
    print(dtypes)
    full_cn = []
    full_dt = [str, int, float]

    arr = np.arange(999).reshape((333, 3))

    for idx in range(7):
        cn = []
        dt_list = []
        di = dict(zip(cn, dt_list))
        di = {'name': int, 'id': str, 'time': float}
        arr = np.arange(999).reshape((333, 3))
        df = blk.create_data_frame("df_" + str(idx), "dataframe", col_dict=di,
                                   data=arr)
        df.definition = "da definition " + str(idx)
        df.force_created_at(np.random.randint(1000000000))
        df.label = "data label " + str(idx)

    nix_file.close()
    # validate(nixfilepath)
    runcpp("readgroups", nixfilepath)

def _test_tags(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "tagtest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    blk = nix_file.create_block("testblock", "blocktype")
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

    nix_file.close()
    # validate(nixfilepath)


def _test_multi_tags(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "mtagtest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    blk = nix_file.create_block("testblock", "blocktype")
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

    nix_file.close()
    # validate(nixfilepath)


def _test_sources(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "sourcetest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    blk = nix_file.create_block("testblock", "sourcetest")
    grp = blk.create_group("testgroup", "sourcetest")
    da = blk.create_data_array("da", "sourcetest",
                               data=np.random.random(10))
    pos = blk.create_data_array("pos", "sourcetest",
                                data=np.random.random(10))
    mtag = blk.create_multi_tag("mtag", "sourcetest", pos)
    grp.data_arrays.append(da)

    for idx in range(20):
        src = blk.create_source("src" + str(idx), "source")
        src_child = src.create_source("child src " + str(idx), "source")

        if (idx % 5) == 0:
            grp.sources.append(src)

        if (idx % 3) == 0:
            mtag.sources.append(src_child)

        if (idx % 8) == 0:
            da.sources.append(src)

    # TODO: Nested sources

    nix_file.close()
    # validate(nixfilepath)


def _test_dimensions(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "dimtest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    blk = nix_file.create_block("testblock", "dimtest")

    da_set = blk.create_data_array("da with set", "datype",
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

    da_alias = blk.create_data_array("da with alias", "datype",
                                     data=np.random.random(19))
    da_alias.unit = "F"
    da_alias.label = "fee fi fo fum"
    da_alias.append_alias_range_dimension()

    da_multi_dim = blk.create_data_array("da with multiple", "datype",
                                         data=np.random.random(30))
    da_multi_dim.append_sampled_dimension(0.1)
    da_multi_dim.append_set_dimension()
    da_multi_dim.append_range_dimension(np.random.random(10))

    nix_file.close()
    # validate(nixfilepath)


def _test_tag_features(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "feattest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    blk = nix_file.create_block("testblock", "feattest")
    da_ref = blk.create_data_array("da for ref", "datype",
                                   nix.DataType.Double,
                                   data=np.random.random(15))
    da_ref.append_sampled_dimension(0.2)
    tag_feat = blk.create_tag("tag for feat", "tagtype", [2])
    tag_feat.references.append(da_ref)

    linktypes = [nix.LinkType.Tagged, nix.LinkType.Untagged,
                 nix.LinkType.Indexed]
    for idx in range(6):
        da_feat = blk.create_data_array("da for feat " + str(idx),
                                        "datype", nix.DataType.Float,
                                        data=np.random.random(12))
        da_feat.append_sampled_dimension(1.0)
        tag_feat.create_feature(da_feat, linktypes[idx % 3])

    nix_file.close()
    # validate(nixfilepath)




def test_multi_tag_features(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "mtagfeattest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    blk = nix_file.create_block("testblock", "mtfeattest")
    index_data = blk.create_data_array(
        "indexed feature data", "test",
        dtype=nix.DataType.Double, shape=(10, 10)
    )
    dim1 = index_data.append_sampled_dimension(1.0)
    dim1.unit = "ms"
    dim2 = index_data.append_sampled_dimension(1.0)
    dim2.unit = "ms"

    data1 = np.zeros((10, 10))
    value = 0.0
    total = 0.0
    for i in range(10):
        value = 100 * i
        for j in range(10):
            value += 1
            data1[i, j] = value
            total += data1[i, j]

    index_data[:, :] = data1

    tagged_data = blk.create_data_array(
        "tagged feature data", "test",
        dtype=nix.DataType.Double, shape=(10, 20, 10)
    )
    dim1 = tagged_data.append_sampled_dimension(1.0)
    dim1.unit = "ms"
    dim2 = tagged_data.append_sampled_dimension(1.0)
    dim2.unit = "ms"
    dim3 = tagged_data.append_sampled_dimension(1.0)
    dim3.unit = "ms"

    data2 = np.zeros((10, 20, 10))
    for i in range(10):
        value = 100 * i
        for j in range(20):
            for k in range(10):
                value += 1
                data2[i, j, k] = value

    tagged_data[:, :, :] = data2

    event_labels = ["event 1", "event 2"]
    dim_labels = ["dim 0", "dim 1", "dim 2"]
    event_array = blk.create_data_array("positions", "test",
                                        data=np.random.random((2, 3)))
    extent_array = blk.create_data_array("extents", "test",
                                         data=np.random.random((2, 3)))
    extent_set_dim = extent_array.append_set_dimension()
    extent_set_dim.labels = event_labels
    extent_set_dim = extent_array.append_set_dimension()
    extent_set_dim.labels = dim_labels

    feature_tag = blk.create_multi_tag("feature_tag", "events",
                                       event_array)
    data_array = blk.create_data_array("featureTest", "test",
                                       nix.DataType.Double, (2, 10, 5))
    data = np.random.random((2, 10, 5))
    data_array[:, :, :] = data

    feature_tag.extents = extent_array

    feature_tag.create_feature(index_data, nix.LinkType.Indexed)
    feature_tag.create_feature(tagged_data, nix.LinkType.Tagged)
    feature_tag.create_feature(index_data, nix.LinkType.Untagged)

    nix_file.close()
    # validate(nixfilepath)


def test_multi_tag_references(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "blocktest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    interval = 0.001
    x = np.arange(0, 10, interval)
    y = np.sin(2*np.pi*x)
    blk = nix_file.create_block("blk", "reftest")
    da = blk.create_data_array("sin", "data", data=y)
    da.unit = "dB"
    dim = da.append_sampled_dimension(interval)
    dim.unit = "s"

    pos = blk.create_data_array("pos1", "positions", data=np.array([[0]]))
    pos.append_set_dimension()
    pos.append_set_dimension()
    pos.unit = "ms"
    ext = blk.create_data_array("ext1", "extents",
                                data=np.array([[2000]]))
    ext.append_set_dimension()
    ext.append_set_dimension()
    ext.unit = "ms"

    mtag = blk.create_multi_tag("sin1", "tag", pos)
    mtag.extents = ext
    mtag.units = ["ms"]
    mtag.references.append(da)

    nix_file.close()
    # validate(nixfilepath)


def test_properties(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "proptest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    sec = nix_file.create_section("test section", "proptest")
    sec.create_property("test property", 0)
    sec.create_property("test str", nix.DataType.String)
    sec.create_property("other property", nix.DataType.Int64)

    sec.create_property("prop Int32", nix.DataType.Int32)
    sec.create_property("prop Int64", nix.DataType.Int64)
    sec.create_property("prop UInt32", nix.DataType.UInt32)
    sec.create_property("prop UInt64", nix.DataType.UInt64)
    sec.create_property("prop Float", nix.DataType.Float)
    sec.create_property("prop Double", nix.DataType.Double)
    sec.create_property("prop String", nix.DataType.String)
    sec.create_property("prop Bool", nix.DataType.Bool)

    sec.props[1].definition = "def"

    sec.props[0].values = [101]
    sec.props[1].values = ["foo", "bar", "baz"]
    sec.props["prop Float"].values = [10.0, 33.3, 1.345, 90.2]

    nix_file.close()
    # validate(nixfilepath)


def test_sections(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "sectiontest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    for idx in range(30):
        sec = nix_file.create_section("test section" + str(idx),
                                      "sectiontest")
        sec.definition = "sec definition " + str(idx)
        sec.repository = "sec repo" + str(idx * 3)

        nested_sec = sec.create_section("nested_section", "sec")
        if (idx % 3) == 0:
            lvl2 = nested_sec.create_section("level 2", "sec")

            if (idx % 12) == 0:
                lvl2.create_section("level 3", "sec")

    block = nix_file.create_block("block", "section test")
    block.metadata = nix_file.sections[0].sections[0].sections[0]

    nix_file.close()
    # validate(nixfilepath)


def test_full_write(tmpdir):
    # Create a fully-featured nix file
    nixfilepath = os.path.join(str(tmpdir), "fulltest.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)
    for idx in range(30):
        sec = nix_file.create_section("test section" + str(idx),
                                      "sectiontest")
        sec.definition = "sec definition " + str(idx)
        sec.repository = "sec repo" + str(idx * 3)

        nested_sec = sec.create_section("nested_section", "sec")
        if (idx % 3) == 0:
            lvl2 = nested_sec.create_section("level 2", "sec")

            if (idx % 12) == 0:
                lvl2.create_section("level 3", "sec")

    block = nix_file.create_block("block", "section test")
    block.metadata = nix_file.sections[0].sections[0].sections[0]

    nix_file.close()
    # validate(nixfilepath)


def test_full_file(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "filetest-writepy.nix")
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.Overwrite)

    block = nix_file.create_block("blockyblock", "ablocktype of thing")
    block.definition = "I am a test block"
    block.force_created_at(1500001000)

    scndblk = nix_file.create_block("I am another block", "void")
    scndblk.definition = "Void block of stuff"
    scndblk.force_created_at(1500002000)

    thrdblk = nix_file.create_block("Block C", "a block of stuff")
    thrdblk.definition = "The third block"
    thrdblk.force_created_at(1500003000)

    for idx, block in enumerate(nix_file.blocks):
        group = block.create_group("grp{:02}0".format(idx), "grp")
        group.definition = "grp{:02}0-grp".format(idx)
        group.force_created_at(block.created_at)
        group = block.create_group("grp{:02}1".format(idx), "grp")
        group.definition = "grp{:02}1-grp".format(idx)
        group.force_created_at(block.created_at)

    block = nix_file.blocks[0]
    da = block.create_data_array("bunchodata", "recordings",
                                 dtype=nix.DataType.Double,
                                 data=[[1, 2, 10], [9, 1, 3]])
    da.definition = "A silly little data array"
    smpldim = da.append_sampled_dimension(0.1)
    smpldim.unit = "ms"
    smpldim.label = "time"
    setdim = da.append_set_dimension()
    setdim.labels = ["a", "b"]
    group = block.groups[0]
    group.data_arrays.append(da)

    df = block.create_data_frame("adataframe", "4-column df",
                                 col_dict={'name': str, 'id': int, 'time': float, 'Adjusted': bool},
                                   data=[["Bob", 9, 11.28, False], ["Jane", 10, 14.37, True]])
    df.append_rows([["Alice", 2, 3.7, False]])

    featda = block.create_data_array("feat-da", "tag-feature",
                                     data=[0.4, 0.41, 0.49, 0.1, 0.1, 0.1])

    tag = block.create_tag("tagu", "tagging", position=[1, 0])
    tag.extent = [1, 10]
    tag.units = ["mV", "s"]
    tag.definition = "tags ahoy"
    tag.references.append(da)
    group.tags.append(tag)
    # TODO: Every other kind of link
    tag.create_feature(featda, nix.LinkType.Untagged)

    mtag = block.create_multi_tag("mtagu", "multi tagging",
                                  positions=block.create_data_array(
                                      "tag-data", "multi-tagger",
                                      data=[[0, 0.1, 10.1]]
                                  ))
    # MultiTag positions array
    block.data_arrays["tag-data"].append_sampled_dimension(0.01)
    block.data_arrays["tag-data"].dimensions[0].unit = "s"
    block.data_arrays["tag-data"].append_set_dimension()

    # MultiTag extents array
    mtag.extents = block.create_data_array("tag-extents", "multi-tagger",
                                           data=[[0.5, 0.5, 0.5]])
    block.data_arrays["tag-extents"].append_sampled_dimension(0.01)
    block.data_arrays["tag-extents"].dimensions[0].unit = "s"
    block.data_arrays["tag-extents"].append_set_dimension()

    da = nix_file.blocks[1].create_data_array("FA001", "Primary data",
                                              dtype=np.int64,
                                              data=[100, 200, 210, 4])
    da.definition = "Some random integers"

    # Source tree
    block = nix_file.blocks[0]
    src = block.create_source("root-source", "top-level-source")
    # point all (block's) data arrays to root-source
    for da in block.data_arrays:
        da.sources.append(src)

    srcd1 = src.create_source("d1-source", "second-level-source")
    src.create_source("d1-source-2", "second-level-source")
    # point first da to d1-source
    block.data_arrays[0].sources.append(srcd1)

    # Metadata
    # 3 root sections
    for name in ["mda", "mdb", "mdc"]:
        nix_file.create_section(name, "root-section")

    sec = nix_file.sections["mdc"]
    # 6 sections under third root section
    for idx in range(6):
        sec.create_section("{:03}-md".format(idx), "d1-section")

    # Point existing objects to metadata sections
    nix_file.blocks[0].metadata = nix_file.sections["mdb"]
    nix_file.blocks[2].metadata = nix_file.sections["mdb"]

    nix_file.blocks[1].data_arrays[0].metadata = nix_file.sections["mda"]
    nix_file.blocks[0].tags[0].metadata = nix_file.sections["mdc"].sections[3]

    # Add Tag and MultiTag to Block 2, Group 0
    block = nix_file.blocks[2]
    group = block.groups[0]
    tag = block.create_tag("POI", "TAG", position=[0, 0])
    tag.extent = [1920, 1080]
    tag.units = ["mm", "mm"]

    png = block.create_data_array("some-sort-of-image?", "png",
                                  shape=(3840, 2160))
    tag.create_feature(png, nix.LinkType.Indexed)

    newmtpositions = block.create_data_array("nu-pos", "multi-tag-positions",
                                             shape=(10, 3),
                                             dtype=nix.DataType.Double)
    newmtag = block.create_multi_tag("nu-mt", "multi-tag (new)",
                                     positions=newmtpositions)
    group.tags.append(tag)
    group.multi_tags.append(newmtag)

    # Data with RangeDimension
    block = nix_file.blocks[2]
    da = block.create_data_array("the ticker", "range-dim-array",
                                 dtype=nix.DataType.Int32,
                                 data=[0, 1, 23])
    da.unit = "uA"
    ticks = np.arange(10, 15, 0.1)
    rdim = da.append_range_dimension(ticks)
    rdim.label = "a range dimension"
    rdim.unit = "s"

    # Alias RangeDimension
    block = nix_file.blocks[1]
    da = block.create_data_array("alias da", "dimticks",
                                 data=np.arange(3, 15, 0.5))
    da.label = "alias dimension label"
    da.unit = "F"
    da.append_alias_range_dimension()

    # All types of metadata
    mdb = nix_file.sections["mdb"]
    proptypesmd = mdb.create_section("prop-test-parent",
                                     "test metadata section")
    numbermd = proptypesmd.create_section("numerical metadata",
                                          "test metadata section")
    numbermd["integer"] = 42
    numbermd["float"] = 4.2
    numbermd["integers"] = [40, 41, 42, 43, 44, 45]
    numbermd["floats"] = [1.1, 10.10]

    othermd = proptypesmd.create_section("other metadata",
                                         "test metadata section")
    othermd["bool"] = True
    othermd["false bool"] = False
    othermd["bools"] = [True, False, True]
    othermd["string"] = "I am a string. Rawr."
    othermd["strings"] = ["one", "two", "twenty"]

    # All types of data
    dtypeblock = nix_file.create_block("datablock", "block of data")

    for n, dt in enumerate(dtypes):
        dtypeblock.create_data_array(str(n), "dtype-test-array",
                                     dtype=dt, data=dt(0))

    nix_file.close()
    runcpp("readfullfile", nixfilepath)
    # validate(nixfilepath)


def check_block_children_counts(block, ngrp, nda, nt, nmt):
    assert ngrp == len(block.groups),\
        "Group count mismatch in Block {}".format(block.name)
    assert nda == len(block.data_arrays),\
        "DataArray count mismatch in Block {}".format(block.name)
    assert nt == len(block.tags),\
        "Tag count mismatch in Block {}".format(block.name)
    assert nmt == len(block.multi_tags),\
        "MultiTag count mismatch in Block {}".format(block.name)


def check_group_children_counts(group, nda, nt, nmt):
    assert nda == len(group.data_arrays),\
        "DataArray count mismatch in Group {}".format(group.name)
    assert nt == len(group.tags),\
        "Tag count mismatch in Group {}".format(group.name)
    assert nmt == len(group.multi_tags),\
        "MultiTag count mismatch in Group {}".format(group.name)


def compare(exp, actual):
    if (isinstance(exp, Iterable) and
            isinstance(actual, Iterable) and not
            isinstance(exp, string_types)):
        assert len(exp) == len(actual),\
            "Expected {}, got {}".format(exp, actual)
        [compare(e, a) for e, a in zip(exp, actual)]
        return
    assert exp == actual, "Expected {}, got {}".format(exp, actual)


def test_full_file_read(tmpdir):
    nixfilepath = os.path.join(str(tmpdir), "filetest-readpy.nix")
    runcpp("writefullfile", nixfilepath)
    nix_file = nix.File.open(nixfilepath, mode=nix.FileMode.ReadOnly)

    # Check object counts
    assert 4 == len(nix_file.blocks), "Block count mismatch"
    check_block_children_counts(nix_file.blocks[0], 2, 4, 1, 1)
    check_block_children_counts(nix_file.blocks[1], 2, 2, 0, 0)
    check_block_children_counts(nix_file.blocks[2], 2, 3, 1, 1)
    check_block_children_counts(nix_file.blocks[3], 0, 12, 0, 0)

    check_group_children_counts(nix_file.blocks[0].groups[0], 1, 1, 0)
    check_group_children_counts(nix_file.blocks[0].groups[1], 0, 0, 0)

    check_group_children_counts(nix_file.blocks[1].groups[0], 0, 0, 0)
    check_group_children_counts(nix_file.blocks[1].groups[1], 0, 0, 0)

    check_group_children_counts(nix_file.blocks[2].groups[0], 0, 1, 1)
    check_group_children_counts(nix_file.blocks[2].groups[1], 0, 0, 0)

    block = nix_file.blocks[0]
    # Check first block attrs before descending
    compare("blockyblock", block.name)
    compare("ablocktype of thing", block.type)
    compare("I am a test block", block.definition)

    block = nix_file.blocks[1]
    # Check second block attrs (no children)
    compare("I am another block", block.name)
    compare("void", block.type)
    compare("Void block of stuff", block.definition)

    for bidx, block in enumerate(nix_file.blocks):
        for gidx, group in enumerate(block.groups):
            compare("grp0{}{}".format(bidx, gidx), group.name)
            compare("grp", group.type)
            compare("group {}".format(gidx), group.definition)
            compare(block.created_at, group.created_at)

    # DataArray
    block = nix_file.blocks[0]
    group = block.groups[0]

    da = block.data_arrays[0]
    compare(da.id, group.data_arrays[0].id)
    compare("bunchodata", da.name)
    compare("recordings", da.type)
    compare("A silly little data array", da.definition)

    # Data
    compare([[1., 2., 10.], [9., 1., 3.]], da[:])
    compare([2, 3], da.shape)
    compare(nix.DataType.Double, da.data_type)

    # DataArray dimensions
    dim = da.dimensions[0]
    compare(nix.DimensionType.Sample, dim.dimension_type)
    compare(0.1, dim.sampling_interval)
    compare("ms", dim.unit)
    compare("time", dim.label)

    dim = da.dimensions[1]
    compare(nix.DimensionType.Set, dim.dimension_type)
    compare(["a", "b"], dim.labels)

    # Tag
    tag = block.tags[0]
    compare("tagu", tag.name)
    compare("tagging", tag.type)
    compare("tags ahoy", tag.definition)
    compare([1, 0], tag.position)
    compare([1, 10], tag.extent)
    compare(["mV", "s"], tag.units)
    compare(da.id, tag.references[0].id)
    compare(group.tags[0].id, tag.id)
    feature = tag.features["feat-da"]
    compare(nix.LinkType.Untagged, feature.link_type)
    compare(feature.data.id, block.data_arrays[1].id)
    compare("feat-da", feature.data.name)
    compare((6,), feature.data.shape)
    compare([0.4, 0.41, 0.49, 0.1, 0.1, 0.1], feature.data[:])

    # MultiTag
    mtag = block.multi_tags[0]
    compare("mtagu", mtag.name)
    compare("multi tagging", mtag.type)
    compare(None, mtag.definition)
    posmt = mtag.positions
    extmt = mtag.extents
    compare(posmt.id, block.data_arrays[posmt.name].id)
    compare(extmt.id, block.data_arrays[extmt.name].id)

    # MultiTag data
    compare("tag-data", posmt.name)
    compare("multi-tagger", posmt.type)
    compare("tag-extents", extmt.name)
    compare("multi-tagger", extmt.type)

    compare([1, 3], posmt.shape)
    compare([[0, 0.1, 10.1]], posmt[:])
    compare(nix.DataType.Double, posmt.data_type)

    compare([1, 3], extmt.shape)
    compare([[0.5, 0.5, 0.5]], extmt[:])
    compare(nix.DataType.Double, extmt.data_type)

    # MultiTag Position and Extent dimensions
    compare(2, len(posmt.dimensions))
    dim = posmt.dimensions[1]
    compare(nix.DimensionType.Set, dim.dimension_type)

    dim = posmt.dimensions[0]
    compare(nix.DimensionType.Sample, dim.dimension_type)
    compare(0.01, dim.sampling_interval)
    compare("s", dim.unit)

    compare(2, len(extmt.dimensions))
    dim = extmt.dimensions[1]
    compare(nix.DimensionType.Set, dim.dimension_type)

    dim = extmt.dimensions[0]
    compare(nix.DimensionType.Sample, dim.dimension_type)
    compare(0.01, dim.sampling_interval)
    compare("s", dim.unit)

    # Tag and MultiTag Block and Group membership
    for idx in range(1, len(nix_file.blocks)):
        assert tag.id not in nix_file.blocks[idx].tags,\
            "Tag found in incorrect Block"
        assert mtag.id not in nix_file.blocks[idx].multi_tags,\
            "MultiTag found in incorrect Block"

    group = block.groups[0]
    assert mtag.id not in group.multi_tags, "MultiTag found in incorrect Group"
    for idx in range(1, len(block.groups)):
        tag.id not in block.groups[idx].tags, "Tag found in incorrect Group"
        mtag.id not in block.groups[idx].multi_tags,\
            "MultiTag found in incorrect Group"

    # Second block DataArray
    block = nix_file.blocks[1]
    da = block.data_arrays[0]
    compare("FA001", da.name)
    compare("Primary data", da.type)
    compare(nix.DataType.Int64, da.data_type)

    # Sources
    block = nix_file.blocks[0]
    compare(1, len(block.sources))
    src = block.sources["root-source"]
    compare("top-level-source", src.type)
    for da in block.data_arrays:
        compare(da.sources[0].id, src.id)

    compare(2, len(src.sources))
    compare("d1-source", src.sources[0].name)
    compare("d1-source-2", src.sources[1].name)
    compare("second-level-source", src.sources[0].type)
    compare("second-level-source", src.sources[1].type)

    for s in src.sources:
        compare(0, len(s.sources))

    da = block.data_arrays[0]
    compare(2, len(da.sources))
    compare(da.sources[1].id, block.sources[0].sources[0].id)

    # Metadata
    # 3 root sections
    compare(3, len(nix_file.sections))
    compare("mda", nix_file.sections[0].name)
    compare("mdb", nix_file.sections[1].name)
    compare("mdc", nix_file.sections[2].name)
    for s in nix_file.sections:
        compare("root-section", s.type)

    mdc = nix_file.sections[2]
    compare(6, len(mdc.sections))
    for idx in range(6):
        compare("d1-section", mdc.sections["{:03d}-md".format(idx)].type)

    mdb = nix_file.sections[1]
    compare(nix_file.blocks[0].metadata.id, mdb.id)
    compare(nix_file.blocks[2].metadata.id, mdb.id)

    compare(nix_file.blocks[1].data_arrays[0].metadata.id,
            nix_file.sections["mda"].id)
    compare(nix_file.blocks[0].tags[0].metadata.id,
            nix_file.sections["mdc"].sections[3].id)

    block = nix_file.blocks[2]
    tag = block.tags[0]
    compare("POI", tag.name)
    compare("TAG", tag.type)
    compare([0, 0], tag.position)
    compare([1920, 1080], tag.extent)
    compare(["mm", "mm"], tag.units)
    compare(tag.id, block.groups[0].tags[0].id)

    feature = tag.features["some-sort-of-image?"]
    compare(nix.LinkType.Indexed, feature.link_type)
    compare(feature.data.id, block.data_arrays[0].id)
    compare("some-sort-of-image?", feature.data.name)
    compare([3840, 2160], feature.data.shape)

    mtag = block.multi_tags[0]
    compare("nu-mt", mtag.name)
    compare("multi-tag (new)", mtag.type)
    posmt = mtag.positions
    compare("nu-pos", posmt.name)
    compare("multi-tag-positions", posmt.type)
    compare([10, 3], posmt.shape)
    compare(nix.DataType.Double, posmt.data_type)
    compare(posmt.id, block.data_arrays[1].id)
    compare(mtag.id, block.groups[0].multi_tags[0].id)

    # Data with range dimension
    block = nix_file.blocks[2]
    da = block.data_arrays["the ticker"]
    compare([0, 1, 23], da[:])
    compare([3], da.shape)
    compare("range-dim-array", da.type)
    compare("uA", da.unit)
    compare(nix.DataType.Int32, da.data_type)
    dim = da.dimensions[0]
    compare(nix.DimensionType.Range, dim.dimension_type)

    # Alias range dimension
    block = nix_file.blocks[1]
    da = block.data_arrays["alias da"]
    compare("dimticks", da.type)
    compare("F", da.unit)
    compare("alias dimension label", da.label)
    compare([24], da.shape)
    dim = da.dimensions[0]
    compare(nix.DimensionType.Range, dim.dimension_type)
    assert dim.is_alias
    compare(da[:], dim.ticks)

    # Metadata types
    mdb = nix_file.sections["mdb"]
    compare(1, len(mdb.sections))
    proptypesmd = mdb.sections["prop-test-parent"]
    compare("test metadata section", proptypesmd.type)
    compare(2, len(proptypesmd.sections))

    numbermd = proptypesmd.sections[0]
    compare("numerical metadata", numbermd.name)
    compare("test metadata section", numbermd.type)
    compare(4, len(numbermd.props))

    prop = numbermd.props["integer"]
    compare(1, len(prop.values))
    compare([42], prop.values)

    prop = numbermd.props["float"]
    compare(1, len(prop.values))
    # TODO: Almost equal
    # compare([4.2], prop.values)

    prop = numbermd.props["integers"]
    compare(6, len(prop.values))
    compare([40+v for v in range(6)], prop.values)

    prop = numbermd.props["floats"]
    compare(2, len(prop.values))
    # TODO: Almost equal

    othermd = proptypesmd.sections[1]
    compare("other metadata", othermd.name)
    compare("test metadata section", othermd.type)
    compare(5, len(othermd.props))

    prop = othermd.props["bool"]
    compare(1, len(prop.values))
    compare([True], prop.values)

    prop = othermd.props["false bool"]
    compare(1, len(prop.values))
    compare([False], prop.values)

    prop = othermd.props["bools"]
    compare(3, len(prop.values))
    compare([True, False, True], prop.values)

    prop = othermd.props["string"]
    compare(1, len(prop.values))
    compare(["I am a string. Rawr."], prop.values)

    prop = othermd.props["strings"]
    compare(3, len(prop.values))
    compare([v for v in ["one", "two", "twenty"]], prop.values)

    # TODO: Check type compatibilities
    # for idx in range(len(dtypes)):
    #     da = block.data_arrays[idx]
    #     dt = dtypes[idx]
    #     compare(dt, da.data_type)
    #     compare([1], da.shape)

    nix_file.close()
    # validate(nixfilepath)
