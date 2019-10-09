from __future__ import (absolute_import, division, print_function)
import nixio as nix
import numpy as np
import os
import unittest
from .tmp import TempDir
# from ..validate import Validate


class TestValidate (unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("validatetest")
        self.testfilename = os.path.join(self.tmpdir.path, "validatetest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block1 = self.file.create_block("blk1", "blk")
        self.block2 = self.file.create_block("blk2", "blk2")
        for blk in self.block1, self.block2:
            for i in range(2):
                blk.create_group("grp{}".format(i), "groups")
            for i in range(4):
                blk.create_data_array("da{}".format(i), "data_arrays",
                                      dtype="float",
                                      data=(1 + np.random.random(5)))
            for i in range(4):
                blk.create_tag("tag{}".format(i), "tags",
                               np.random.random(1))
            for i in range(4):
                blk.create_multi_tag("mt{}".format(i), "multi_tags",
                                     blk.data_arrays[i])

        self.file.create_section("sec1", "test")

    def tearDown(self):
        self.file.close()
        self.tmpdir.cleanup()

    def test_check_file(self):
        res = self.file.validate()
        assert self.file not in res["errors"]
        assert self.file not in res["warnings"]
        self.file.force_created_at(0)
        res = self.file.validate()
        assert res["errors"][self.file] == ["date is not set"]

    def test_check_blocks(self):
        res = self.file.validate()
        block = self.block1
        assert block not in res["errors"]

        block._h5group.set_attr("name", None)
        res = self.file.validate()
        assert res["errors"][block] == ["no name set"]

        block._h5group.set_attr("type", None)
        res = self.file.validate()
        actual = sorted(res["errors"][block])
        expected = sorted(["no name set", "no type set"])
        assert actual == expected
        assert len(res["warnings"]) == 0

    def test_check_groups(self):
        group1 = self.block1.groups[0]
        group2 = self.block2.groups[1]
        group1._h5group.set_attr("name", None)
        res = self.file.validate()
        assert res["errors"][group1] == ["no name set"]
        assert group2 not in res["errors"]

        group2._h5group.set_attr("name", None)
        res = self.file.validate()
        assert res["errors"][group2] == ["no name set"]

        assert group1 not in res["warnings"]
        assert group2 not in res["warnings"]

        group2._h5group.set_attr("type", None)
        res = self.file.validate()
        actual = sorted(res["errors"][group2])
        expected = sorted(["no name set", "no type set"])
        assert actual == expected
        assert len(res["warnings"]) == 0

    def test_check_data_arrays(self):
        expected_errors = list()
        expected_warnings = list()
        somedata = np.random.randint(10, size=(5, 5))
        da1 = self.block1.create_data_array("data", "type",
                                            dtype=nix.DataType.Int32,
                                            data=somedata)
        da1.append_range_dimension([1, 2, 3, 4, 5, 6, 7, 8, 9])
        expected_errors.append(
            "number of ticks in RangeDimension (1) differs from the number "
            "of data entries along the corresponding data dimension"
        )
        setdim = da1.append_set_dimension()
        setdim.labels = ["A", "B", "C", "D"]
        expected_errors.append(
            "number of labels in SetDimension (2) differs from the number "
            "of data entries along the corresponding data dimension"
        )
        da1._h5group.set_attr("type", None)
        expected_errors.append("no type set")
        da1._h5group.set_attr("expansion_origin", 0.11)  # poly not set
        expected_warnings.append(
            "expansion origin for calibration is set, "
            "but polynomial coefficients are missing"
        )

        res = self.file.validate()

        da_err = res["errors"][da1]
        da_warn = res["warnings"][da1]

        assert sorted(da_err) == sorted(expected_errors)
        assert sorted(da_warn) == sorted(expected_warnings)

        da2 = self.block1.data_arrays[1]
        setdim = da2.append_set_dimension()
        setdim.labels = ["A", "B", "C", "D", "E"]
        da2.polynom_coefficients = [0.1, 0.2]
        res = self.file.validate()
        da_warn = res["warnings"][da2]
        assert da_warn == ["polynomial coefficients for calibration are set, "
                           "but expansion origin is missing"]

        da3 = self.block1.data_arrays[0]
        res = self.file.validate()
        da_err = res["errors"][da3]
        assert da_err == ["data dimensionality does not match number of "
                          "defined dimensions"]

    def test_check_tags(self):
        tag1 = self.block1.tags[0]
        tag1.position = []
        self.validator.check_tag(tag1, 0, 0)
        tagerr = self.validator.errors['blocks'][0]['tags'][0]['errors']
        assert tagerr == ['Position is not set!']

        tag2 = self.block1.tags[1]
        tag2.units = ['abc']
        self.validator.check_tag(tag2, 1, 0)
        tagerr = self.validator.errors['blocks'][0]['tags'][1]['errors']
        assert tagerr == ['Invalid unit']

        tag3 = self.block1.tags[2]
        da1 = self.block1.data_arrays[0]
        da1.append_range_dimension([1, 2, 3, 4, 5, 6, 7, 8, 9])
        da1.dimensions[0]._h5group.set_attr("unit", "s")
        da1.append_sampled_dimension(0.5)
        da1.dimensions[1]._h5group.set_attr("unit", "A")
        tag3.references.append(da1)
        tag3.units = ['A', 'mV']
        self.validator.check_tag(tag3, 2, 0)
        assert self.validator.errors['blocks'][0]['tags'][2]['errors'] == [
            'References and tag units mismatched']

        tag4 = self.block1.tags[3]
        da2 = self.block1.data_arrays[1]
        da3 = self.block1.data_arrays[2]
        tag4.references.append(da2)
        tag4.references.append(da3)
        tag4.extent = [1, 1]
        tag4.position = [0.5, 0.5]
        self.validator.check_tag(tag4, 3, 0)
        tag_dim_warn1 = ("Number of extent and dimensionality of reference "
                         "do not match")
        tag_dim_warn2 = ("Number of position and dimensionality of reference "
                         "do not match")
        tagerr = self.validator.errors['blocks'][0]['tags'][3]['errors']
        assert tag_dim_warn2 in tagerr
        assert tag_dim_warn1 in tagerr

        tag5 = self.block2.tags[0]
        da2 = self.block1.data_arrays[1]
        da2.append_range_dimension([1, 2, 3, 4, 5, 6, 7, 8, 9])
        da2.dimensions[0]._h5group.set_attr("unit", "s")
        da2.append_sampled_dimension(0.5)
        da2.dimensions[1]._h5group.set_attr("unit", None)
        tag5.references.append(da2)
        self.validator.check_tag(tag5, 0, 1)
        assert self.validator.errors['blocks'][1]['tags'][0]['errors'] == [
            'Some dimensions of references have no units']

    def test_check_multi_tag(self):
        mt1 = self.block1.multi_tags[0]
        da1 = self.block1.create_data_array(name='test1', array_type='t',
                                            dtype='float', data=0)
        mt1.extents = da1
        self.validator.check_multi_tag(mt1, 0, 0)
        assert self.validator.errors['blocks'][0]['multi_tags'][0]['errors']\
            == ['Number of entries in positions and extents do not match']

        # test for pos & extent with multiple dimensions
        mt2 = self.block1.multi_tags[1]
        da2 = self.block1.create_data_array(name='test2a', array_type='t',
                                            dtype='float',
                                            data=np.random.random((6, 5)))
        da3 = self.block1.create_data_array(name='test2b', array_type='t',
                                            dtype='float',
                                            data=np.random.random((5, 8)))
        da4 = self.block1.create_data_array(name='test2c', array_type='t',
                                            dtype='float',
                                            data=np.random.random((5, 4)))
        da5 = self.block1.create_data_array(name='test2d', array_type='t',
                                            dtype='float',
                                            data=np.random.random((5, 3)))
        mt2.references.append(da2)
        mt2.references.append(da3)
        mt2.positions = da5
        mt2.extents = da4
        self.validator.check_multi_tag(mt2, 1, 0)
        warn1 = "The number of reference and position entries do not match"
        warn2 = "The number of reference and extent entries do not match"
        # pos-extent-mismatch warning exist but not assert
        # change shape of da4/5 to elim warning
        mterr = self.validator.errors['blocks'][0]['multi_tags'][1]['errors']
        assert warn1 in mterr
        assert warn2 in mterr

        # test for pos & extent with only ONE dimensions
        mt3 = self.block1.multi_tags[2]
        da6 = self.block1.create_data_array(name='test3a', array_type='t',
                                            dtype='float',
                                            data=np.random.random(5))
        da7 = self.block1.create_data_array(name='test3b', array_type='t',
                                            dtype='float',
                                            data=np.random.random((3, 3)))
        mt3.positions = da6
        mt3.extents = da6
        mt3.references.append(da7)
        self.validator.check_multi_tag(mt3, 2, 0)
        mterr = self.validator.errors['blocks'][0]['multi_tags'][2]['errors']
        assert warn1 in mterr
        assert warn2 in mterr

        # test for ext and pos dimensionality
        mt4 = self.block1.multi_tags[3]
        da8 = self.block1.create_data_array(name='test3c', array_type='t',
                                            dtype='float',
                                            data=np.random.random((5, 3, 4)))
        mt4.positions = da8
        mt4.extents = da8
        self.validator.check_multi_tag(mt4, 3, 0)
        assert "Positions should not have more than 2 dimensions" \
               in self.validator.errors['blocks'][0]['multi_tags'][3]['errors']
        assert "Extents should not have more than 2 dimensions" \
               in self.validator.errors['blocks'][0]['multi_tags'][3]['errors']

        # test for units
        mt5 = self.block2.multi_tags[0]
        mt5.units = ['s', 'abc']
        da9 = self.block2.data_arrays[0]
        mt5.references.append(da9)
        da9.append_range_dimension([1, 2, 3, 4, 5, 6, 7, 8, 9])
        da9.dimensions[0]._h5group.set_attr("unit", "mV")
        self.validator.check_multi_tag(mt5, 0, 1)
        mtagerr = self.validator.errors['blocks'][1]['multi_tags'][0]['errors']
        assert "Invalid unit" in mtagerr
        assert "References and multi_tag units mismatched" in mtagerr

        # 2nd test for units
        da9.dimensions[0]._h5group.set_attr("unit", "ms")
        mt5.units = ['s']
        self.validator.check_multi_tag(mt5, 0, 1)
        mtagerr = self.validator.errors['blocks'][1]['multi_tags'][0]['errors']
        assert mtagerr == []

    def test_check_section(self):  # only have check for basics now
        sec1 = self.file.sections[0]
        sec1._h5group.set_attr("type", None)
        self.validator.check_section(sec1, 0)
        err = self.validator.errors['sections'][0]['errors']
        assert "Type of Section is missing" in err

    def test_check_props(self):
        # check1
        section = self.file.sections[0]
        prop = section.create_property("prop1", [1, 2, 3, 4])
        self.validator.form_dict()
        # check2
        prop1 = section.create_property("prop2", values_or_dtype=[1, 2, 3, 4])
        prop1.delete_values()
        prop1._h5group.set_attr('name', None)
        # check3
        prop2 = section.create_property("prop3", values_or_dtype=[1, 2, 3, 4])
        prop2.unit = "invalidu"
        self.validator.form_dict()
        self.validator.check_property(prop, 0, 0)  # check1
        err = self.validator.errors['sections'][0]['props'][0]['errors']
        assert "Unit is not set" in err
        # check2 - nameerr but no uniterr
        self.validator.check_property(prop1, 1, 0)
        err = self.validator.errors['sections'][0]['props'][1]['errors']
        assert err == ['Name is not set!']
        self.validator.check_property(prop2, 2, 0)  # check3
        err = self.validator.errors['sections'][0]['props'][2]['errors']
        assert 'Unit is not valid!' in err

    def test_check_features(self):
        pass  # RuntimeError will be raised, so no need for test

    def test_range_dim(self):
        err_dict = self.validator.errors['blocks'][0]['data_arrays']
        # check1
        da1 = self.block1.data_arrays[0]
        rdim1 = da1.append_range_dimension([0.55, 0.10, 0.1])
        # for dims and prop test we need to form_dict again
        self.validator.form_dict()
        rdim1._h5group.set_attr('dimension_type', 'set')
        # check2
        rdim2 = da1.append_range_dimension([])
        rdim2._h5group.set_attr("unit", "m/s")  # compound unit

        self.validator.form_dict()
        self.validator.check_range_dim(rdim1, 0, 0, 0)  # check1
        err = err_dict[0]['dimensions'][0]['errors']
        assert "Dimension type is not correct!" in err
        assert "Ticks are not sorted!" in err
        self.validator.check_range_dim(rdim2, 1, 0, 0)  # check2
        err = err_dict[0]['dimensions'][1]['errors']
        assert "Ticks need to be set for range dimensions" in err
        assert "Unit must be atomic, not composite!" in err

    def test_sample_dim(self):
        # check1
        da1 = self.block1.data_arrays[0]
        sdim1 = da1.append_sampled_dimension(sampling_interval=0.5)
        sdim1._h5group.set_attr('dimension_type', 'set')
        sdim1.offset = 0.1

        # check2
        sdim2 = da1.append_sampled_dimension(sampling_interval=-0.5)
        sdim2.unit = "m/s"

        self.validator.form_dict()
        self.validator.check_sampled_dim(sdim1, 0, 0, 0)  # check1
        da = self.validator.errors['blocks'][0]['data_arrays'][0]
        err = da['dimensions'][0]['errors']
        assert "Dimension type is not correct!" in err
        assert "Offset is set, but no unit set!" in err
        self.validator.check_sampled_dim(sdim2, 1, 0, 0)  # check2
        err = da['dimensions'][1]['errors']
        assert "Unit must be atomic, not composite!" in err
        assert "SamplingInterval is not set to valid value (> 0)!" in err

    def test_set_dim(self):
        da1 = self.block1.data_arrays[0]
        setdim1 = da1.append_set_dimension()
        setdim1._h5group.set_attr('dimension_type', 'range')
        self.validator.form_dict()
        self.validator.check_set_dim(setdim1, 0, 0, 0)
        da = self.validator.errors['blocks'][0]['data_arrays'][0]
        dimerr = da['dimensions'][0]['errors']
        assert "Dimension type is not correct!" in dimerr

    def test_sources(self):
        da1 = self.block1.data_arrays[0]
        src1 = self.block1.create_source("src1", "testing_src")
        da1.sources.append(src1)
        src1._h5group.set_attr('name', None)
        self.validator.form_dict()
        self.validator.check_sources(src1, 0)
        err = self.validator.errors['blocks'][0]['sources']
        assert "Name of Source is missing" in err
