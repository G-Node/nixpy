from __future__ import (absolute_import, division, print_function)
import nixio as nix
import numpy as np
import os
import unittest
from .tmp import TempDir

VE = nix.validator.ValidationError
VW = nix.validator.ValidationWarning


class TestValidate (unittest.TestCase):

    def setUp(self):
        # Create completely valid objects and break for each test
        self.tmpdir = TempDir("validatetest")
        self.testfilename = os.path.join(self.tmpdir.path, "validatetest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        for bidx in range(2):
            # Block
            blk = self.file.create_block("block-{}".format(bidx),
                                         "validation-test.block")
            for gidx in range(2):
                # Groups
                blk.create_group("group-{}".format(gidx),
                                 "validation-test.group")

            # DataArrays + Dimensions
            da1d = blk.create_data_array("data-1d",
                                         "validation-test.data_array",
                                         dtype=nix.DataType.Float,
                                         data=np.random.random(5))
            rdim = da1d.append_range_dimension(ticks=[0.1, 0.2, 1.5, 2.4, 3.0])
            rdim.unit = "ms"

            da2d = blk.create_data_array("data-2d",
                                         "validation-test.data_array",
                                         dtype=nix.DataType.Float,
                                         data=np.random.random((2, 10)))
            setdim = da2d.append_set_dimension()
            setdim.labels = ("A", "B")
            da2d.append_sampled_dimension(0.1)

            da3d = blk.create_data_array("data-3d",
                                         "validation-test.data_array",
                                         dtype=nix.DataType.Float,
                                         data=np.random.random((4, 2, 10)))
            setdim = da3d.append_set_dimension()
            setdim.labels = ("1", "2", "3", "4")
            da3d.append_set_dimension()  # set dim without labels
            smpldim = da3d.append_sampled_dimension(0.05)
            smpldim.unit = "s"

            # Tags + References + Features
            tag = blk.create_tag("tag", "validation-test.tag",
                                 position=(1, 1, 1))
            tag.extent = (2, 1, 5)
            tag.references.append(blk.data_arrays["data-3d"])
            tag.units = ("", "", "ms")

            pos1d = blk.create_data_array(
                "pos-1d", "validation-test.multi_tag.positions",
                data=[0, 1, 10, 20]
            )
            pos1d.append_set_dimension()

            tagwf = blk.create_tag("tag-wf", "validation-test.tag",
                                   position=(1, 3))
            tag_feat_data = blk.create_data_array(
                "feat-1", "validation-test.tag-feature", data=[1]
            )
            tag_feat_data.append_set_dimension()
            tagwf.create_feature(tag_feat_data, nix.LinkType.Untagged)

            # MultiTags + References + Features
            mtag1d = blk.create_multi_tag(
                "mtag1d", "validation-test.multi_tag", positions=pos1d
            )
            mtag1d.references.append(da1d)
            mtag1d.units = ("s",)

            pos2d = blk.create_data_array(
                "pos-2d", "validation-test.multi_tag.positions",
                data=[(10, 2, 100), (20, 5, 101)]
            )
            pos2d.append_set_dimension()
            pos2d.append_set_dimension()

            ext2d = blk.create_data_array(
                "ext-3d", "validation-test.multi_tag.extents",
                data=[(1, 1, 1), (5, 5, 5)]
            )
            ext2d.append_set_dimension()
            ext2d.append_set_dimension()
            mtag2d = blk.create_multi_tag(
                "mtag2d", "validation-test.multi_tag", positions=pos2d
            )
            mtag2d.extents = ext2d
            mtag2d.references.append(da3d)
            mtag2d.units = ("", "", "us")

            poswf = blk.create_data_array(
                "pos-wf", "validation-test.multi_tag.feature", data=[42]
            )
            poswf.append_set_dimension()
            mtagwf = blk.create_multi_tag(
                "mtag-wf", "validation-test.multi_tag.feature",
                positions=poswf
            )
            mtag_feat_data = blk.create_data_array(
                "feat-2", "validation-test.tag-feature", data=[4, 2]
            )
            mtag_feat_data.append_set_dimension()
            mtagwf.create_feature(mtag_feat_data, nix.LinkType.Untagged)

            # Sources
            # Go 3 levels deep (with N = 3:2:1)
            typestr = "validation-test.sources"
            for idx in range(3):
                isrc = blk.create_source("{}:{}".format(blk.name, idx),
                                         typestr)
                for jdx in range(2):
                    jsrc = isrc.create_source("{}:{}".format(isrc.name, jdx),
                                              typestr)
                    jsrc.create_source("{}:0".format(jsrc.name),
                                       typestr)

        # Sections
        # Go 3 levels deep (with N = 4:2:2)
        # 3 props per Section

        def attach_props(section):
            section.create_property("intprop", "prop-type", 10).unit = "s"
            section.create_property("strprop", "prop-type", 0.1).unit = "mA"
        typestr = "validation-test.sections"
        for idx in range(4):
            isec = self.file.create_section("{}:{}".format(blk.name, idx),
                                            typestr)
            attach_props(isec)
            for jdx in range(2):
                jsec = isec.create_section("{}:{}".format(isec.name, jdx),
                                           typestr)
                for kdx in range(2):
                    jsec.create_section("{}:{}".format(jsec.name, kdx),
                                        typestr)

    def tearDown(self):
        self.file.close()
        self.tmpdir.cleanup()

    def test_all_valid(self):
        res = self.file.validate()
        assert not res["errors"], self.print_all_results(res)
        assert not res["warnings"], self.print_all_results(res)

    def test_check_file(self):
        self.file.version = tuple()
        res = self.file.validate()
        assert VW.NoVersion in res["warnings"][self.file]

        self.file.format = ""
        res = self.file.validate()
        assert VW.NoFormat in res["warnings"][self.file]

    def test_check_block(self):
        block = self.file.blocks[0]
        block._h5group.set_attr("name", None)
        res = self.file.validate()
        assert res["errors"][block] == [VE.NoName]

        block._h5group.set_attr("type", None)
        res = self.file.validate()
        actual = sorted(res["errors"][block])
        expected = sorted([VE.NoName, VE.NoType])
        assert actual == expected
        assert len(res["warnings"]) == 0

    def test_check_group(self):
        group1 = self.file.blocks[0].groups[0]
        group2 = self.file.blocks[1].groups[0]
        group1._h5group.set_attr("name", None)
        res = self.file.validate()
        assert res["errors"][group1] == [VE.NoName]
        assert group2 not in res["errors"]

        group2._h5group.set_attr("name", None)
        res = self.file.validate()
        assert res["errors"][group2] == [VE.NoName]

        assert group1 not in res["warnings"]
        assert group2 not in res["warnings"]

        group2._h5group.set_attr("type", None)
        res = self.file.validate()
        actual = sorted(res["errors"][group2])
        expected = sorted([VE.NoName, VE.NoType])
        assert actual == expected
        assert len(res["warnings"]) == 0

    def test_check_data_array_wrong_ticks(self):
        expmsg = VE.RangeDimTicksMismatch.format(1)
        da = self.file.blocks[0].data_arrays["data-1d"]
        rdim = da.dimensions[0]
        rdim.ticks = [10]
        res = self.file.validate()
        assert res["errors"][da] == [expmsg]

    def test_check_data_array_wrong_labels(self):
        expmsg = VE.SetDimLabelsMismatch.format(1)
        da = self.file.blocks[0].data_arrays["data-2d"]
        setdim = da.dimensions[0]
        setdim.labels = ["-"]
        res = self.file.validate()
        assert res["errors"][da] == [expmsg]

    def test_check_data_array_coefficients(self):
        da1 = self.file.blocks[0].data_arrays["data-1d"]
        da1.expansion_origin = 0.7

        da2 = self.file.blocks[1].data_arrays["data-1d"]
        da2.polynom_coefficients = [2, 4]

        res = self.file.validate()
        warnings = res["warnings"]
        assert warnings[da1] == [VW.NoPolynomialCoefficients]
        assert warnings[da2] == [VW.NoExpansionOrigin]

    def test_check_data_array_bad_dims(self):
        da = self.file.blocks[1].data_arrays["data-3d"]
        da.append_set_dimension()
        res = self.file.validate()
        assert res["errors"][da] == [VE.DimensionMismatch]

    def test_check_data_array_invalid_unit(self):
        da = self.file.blocks[1].data_arrays["data-1d"]
        da.unit = "whatevz"
        res = self.file.validate()
        assert res["warnings"][da] == [VW.InvalidUnit]

    def test_incorrect_dim_index(self):
        da = self.file.blocks[1].data_arrays["data-1d"]
        da.delete_dimensions()
        dimgroup = da._h5group.open_group("dimensions")
        # This wont work if we ever change the internals
        nix.SetDimension._create_new(dimgroup, "10")
        res = self.file.validate()
        assert VE.IncorrectDimensionIndex.format(1, 10) in res["errors"][da]

    def test_invalid_dim_index(self):
        da = self.file.blocks[1].data_arrays["data-1d"]
        da.delete_dimensions()
        dimgroup = da._h5group.open_group("dimensions")
        # This wont work if we ever change the internals
        nix.SetDimension._create_new(dimgroup, "-1")
        res = self.file.validate()
        assert VE.InvalidDimensionIndex.format(1) in res["errors"][da]

    def test_check_tag_no_pos(self):
        tag = self.file.blocks[0].tags[0]
        tag.position = []
        res = self.file.validate()
        tagerr = res["errors"][tag]
        # will also report mismatch in dimensions with reference
        assert "position is not set" in tagerr

    def test_check_tag_mismatch_dim(self):
        tag = self.file.blocks[0].tags[0]
        tag.position = [4, 3, 2, 1]
        res = self.file.validate()
        tagerr = res["errors"][tag]
        assert VE.PositionDimensionMismatch in tagerr

    def test_check_tag_invalid_unit(self):
        tag = self.file.blocks[0].tags[0]
        tag.units = ['abc']
        res = self.file.validate()
        tagerr = res["errors"][tag]
        assert VE.InvalidUnit in tagerr

    def test_check_tag_mismatch_units(self):
        tag = self.file.blocks[0].tags[0]
        tag.units = ("V", "A")
        res = self.file.validate()
        tagerr = res["errors"][tag]
        assert VE.ReferenceUnitsMismatch in tagerr

        tag.units = ("V", "A", "L")
        res = self.file.validate()
        tagerr = res["errors"][tag]
        assert VE.ReferenceUnitsIncompatible in tagerr

    def test_check_tag_pos_ext_mismatch(self):
        tag = self.file.blocks[0].tags[0]
        tag.extent = [100]

        res = self.file.validate()
        tagerr = res["errors"][tag]
        assert VE.ExtentDimensionMismatch in tagerr

    def test_check_multi_tag_no_pos(self):
        blk = self.file.blocks[0]
        mtag = blk.multi_tags["mtag1d"]
        mtag.positions = blk.create_data_array("empty", "bork", data=[])
        res = self.file.validate()
        mtagerr = res["errors"][mtag]
        # will also report mismatch in dimensions with reference
        assert VE.NoPositions in mtagerr

    def test_check_multi_tag_mismatch_dim(self):
        blk = self.file.blocks[0]

        # 2d tag positions on 2d data, with wrong positions length
        mtag = blk.multi_tags["mtag2d"]
        okpos = mtag.positions
        mtag.positions = blk.create_data_array("wrong dim len", "bork",
                                               data=[(1, 1), (2, 2)])
        res = self.file.validate()
        mtagerr = res["errors"][mtag]
        assert VE.PositionsDimensionMismatch in mtagerr

        # 1d tag positions on 2d data
        mtag.positions = blk.create_data_array("1d v 2d", "bork",
                                               data=[1, 2])
        res = self.file.validate()
        mtagerr = res["errors"][mtag]
        assert VE.PositionsDimensionMismatch in mtagerr

        # valid tag positions on 2d data, 1d extents
        mtag.positions = okpos
        mtag.extents = blk.create_data_array("1d extents", "bork",
                                             data=[1, 2])
        res = self.file.validate()
        mtagerr = res["errors"][mtag]
        assert VE.ExtentsDimensionMismatch in mtagerr

    def test_check_multi_tag_invalid_unit(self):
        blk = self.file.blocks[0]
        mtag = blk.multi_tags["mtag2d"]
        mtag.units = ['abc']
        res = self.file.validate()
        tagerr = res["errors"][mtag]
        assert VE.InvalidUnit in tagerr

    def test_check_multi_tag_mismatch_units(self):
        mtag = self.file.blocks[0].multi_tags["mtag2d"]
        mtag.units = ("V", "A")
        res = self.file.validate()
        tagerr = res["errors"][mtag]
        assert VE.ReferenceUnitsMismatch in tagerr

        mtag.units = ("V", "A", "L")
        res = self.file.validate()
        tagerr = res["errors"][mtag]
        assert VE.ReferenceUnitsIncompatible in tagerr

    def test_check_multi_tag_pos_ext_mismatch(self):
        blk = self.file.blocks[0]
        mtag = blk.multi_tags["mtag2d"]
        mtag.extents = blk.create_data_array("wrong dim", "bork",
                                             data=[(1, 1), (2, 2)])

        res = self.file.validate()
        mtagerr = res["errors"][mtag]
        assert VE.PositionsExtentsMismatch in mtagerr

    def test_check_source(self):
        # just break one of the deepest Sources
        def get_deepest_source(sources):
            for source in sources:
                if not source.sources:
                    return source
                return get_deepest_source(source.sources)

        source = get_deepest_source(self.file.blocks[0].sources)
        source._h5group.set_attr("name", None)
        source._h5group.set_attr("type", None)

        res = self.file.validate()
        assert len(res["errors"][source]) == 2
        assert len(res["warnings"]) == 0
        assert sorted(res["errors"][source]) == sorted([VE.NoName, VE.NoType])

    def test_check_section(self):
        # just break one of the deepest Sections
        def get_deepest_section(sections):
            for section in sections:
                if not section.sections:
                    return section
                return get_deepest_section(section.sections)

        section = get_deepest_section(self.file.sections)
        section._h5group.set_attr("name", None)
        section._h5group.set_attr("type", None)

        res = self.file.validate()
        assert len(res["errors"][section]) == 2
        assert len(res["warnings"]) == 0
        assert sorted(res["errors"][section]) == sorted([VE.NoName, VE.NoType])

    def test_check_property(self):
        section = self.file.sections[0]
        prop = section.props[0]
        prop._h5group.set_attr("name", None)
        res = self.file.validate()
        errmsg = "property 0: {}".format(VE.NoName)
        assert res["errors"][section] == [errmsg]

        prop = section.props[1]
        prop.unit = None
        res = self.file.validate()
        warnmsg = "property 1: {}".format(VW.NoUnit)
        assert res["warnings"][section] == [warnmsg]

    def test_check_range_dim_no_ticks(self):
        da = self.file.blocks[1].data_arrays["data-1d"]
        dim = da.dimensions[0]
        dim.ticks = []
        res = self.file.validate()
        assert VE.NoTicks.format(1) in res["errors"][da]

    def test_check_range_dim_invalid_unit(self):
        da = self.file.blocks[1].data_arrays["data-1d"]
        dim = da.dimensions[0]
        dim.unit = "sillyvolts"
        res = self.file.validate()
        assert VE.InvalidDimensionUnit.format(1) in res["errors"][da]

    def test_check_range_dim_unsorted_ticks(self):
        da = self.file.blocks[1].data_arrays["data-1d"]
        dim = da.dimensions[0]
        dim._h5group.write_data("ticks", [10, 3, 1])
        res = self.file.validate()
        assert VE.UnsortedTicks.format(1) in res["errors"][da]

    def test_check_sampled_dim_no_interval(self):
        da = self.file.blocks[1].data_arrays["data-2d"]
        dim = da.dimensions[1]
        dim.sampling_interval = None
        res = self.file.validate()
        assert VE.NoSamplingInterval.format(2) in res["errors"][da]

    def test_check_sampled_dim_bad_interval(self):
        da = self.file.blocks[1].data_arrays["data-2d"]
        dim = da.dimensions[1]
        dim.sampling_interval = -1
        res = self.file.validate()
        assert VE.InvalidSamplingInterval.format(2) in res["errors"][da]

    def test_check_sampled_dim_bad_unit(self):
        da = self.file.blocks[1].data_arrays["data-2d"]
        dim = da.dimensions[1]
        dim.unit = "sillyamps"
        res = self.file.validate()
        assert VE.InvalidDimensionUnit.format(2) in res["errors"][da]

    def test_check_sampled_dim_no_unit(self):
        da = self.file.blocks[1].data_arrays["data-2d"]
        dim = da.dimensions[1]
        dim.unit = None
        dim.offset = 10
        res = self.file.validate()
        assert VW.OffsetNoUnit.format(2) in res["warnings"][da]
