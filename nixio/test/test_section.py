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
import nixio as nix
from .tmp import TempDir


class TestSections(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("sectiontest")
        self.testfilename = os.path.join(self.tmpdir.path, "sectiontest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.section = self.file.create_section("test section",
                                                "recordingsession")
        self.other = self.file.create_section("other section",
                                              "recordingsession")

    def tearDown(self):
        del self.file.sections[self.section.id]
        del self.file.sections[self.other.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_section_eq(self):
        assert self.section == self.section
        assert not self.section == self.other
        assert self.section is not None

    def test_section_id(self):
        assert self.section.id is not None

        # Check setting id on section via file create
        oid = "4a6e8483-0a9a-464d-bdd9-b39818334bcd"
        sec = self.file.create_section("assign id", "sec type", oid)
        assert sec.id == oid

        nonid = "I am not a proper uuid"
        sec = self.file.create_section("invalid id", "sec type", nonid)
        assert sec.id != nonid

        # Check setting id on section via section create
        oid = "4a6e8483-0a9a-464d-bdd9-b39818334bcd"
        sub_sec = sec.create_section("assign id", "sec type", oid)
        assert sub_sec.id == oid

        nonid = "I am not a proper uuid"
        sub_sec = sec.create_section("invalid id", "sec type", nonid)
        assert sub_sec.id != nonid

    def test_section_name(self):
        assert self.section.name is not None

    def test_section_type(self):
        def set_none():
            self.section.type = None

        assert self.section.type is not None
        self.assertRaises(Exception, set_none)

        self.section.type = "foo type"
        assert self.section.type == "foo type"

    def test_section_definition(self):
        assert self.section.definition is None

        self.section.definition = "definition"
        assert self.section.definition == "definition"

        self.section.definition = None
        assert self.section.definition is None

    def test_section_repository(self):
        assert self.section.repository is None

        self.section.repository = "repository"
        assert self.section.repository == "repository"

        self.section.repository = None
        assert self.section.repository is None

    def test_property_reference(self):
        assert self.section.reference is None

        self.section.reference = "reference"
        assert self.section.reference == "reference"

        self.section.reference = None
        assert self.section.reference is None
        self.section.reference = None

    def test_section_sections(self):
        assert len(self.section.sections) == 0

        child = self.section.create_section("test section", "electrode")
        assert child.parent == self.section

        assert len(self.section.sections) == 1

        assert child in self.section.sections
        assert child.id in self.section.sections
        assert "notexist" not in self.section.sections

        assert child.id == self.section.sections[0].id
        assert child.id == self.section.sections[-1].id

        del self.section.sections[0]

        assert len(self.section.sections) == 0

        self.section['easy subsection'] = nix.S('electrode')
        subject = self.section['subject'] = nix.S('subject')

        assert self.section['subject'] == subject
        assert self.section['subject'].id == subject.id
        assert('easy subsection' in
               [v.name for k, v in self.section.sections.items()])
        assert 'easy subsection' in self.section.sections
        assert self.section['easy subsection'].name == 'easy subsection'

    def test_section_find_sections(self):
        for i in range(2):
            self.section.create_section("level1-p0-s" + str(i), "dummy")
        for i in range(2):
            self.section.sections[0].create_section("level2-p1-s" + str(i),
                                                    "dummy")
        for i in range(2):
            self.section.sections[1].create_section("level2-p2-s" + str(i),
                                                    "dummy")
        for i in range(2):
            self.section.sections[0].sections[0].create_section(
                "level3-p1-s" + str(i), "dummy"
            )

        assert len(self.section.find_sections()) == 9
        assert len(self.section.find_sections(limit=1)) == 3
        assert(len(self.section.find_sections(
            filtr=lambda x: "level2-p1-s" in x.name)) == 2
               )
        assert(len(self.section.find_sections(
            filtr=lambda x: "level2-p1-s" in x.name, limit=1)) == 0
               )

        assert len(self.section.find_related()) == 3
        assert len(self.section.sections[0].find_related()) == 5

    def test_section_properties(self):
        assert len(self.section) == 0

        prop = self.section.create_property("test prop", nix.DataType.String)

        assert len(self.section) == 1

        for p in self.section:
            assert p in self.section

        assert "test prop" in self.section
        assert "notexist" not in self.section
        assert self.section["test prop"] is not None
        # NOTE: the following raises KeyError: Do we want it to return None?
        # assert self.section["notexist"] is None

        assert len(self.section.inherited_properties()) == 1

        assert prop in self.section
        assert prop.id in self.section
        assert prop.name in self.section
        assert "notexist" not in self.section

        props = dict(self.section.items())
        assert props["test prop"] == prop

        assert prop.id == self.section.props[0].id
        assert prop.id == self.section.props[-1].id

        # easy prop creation
        self.section['ep_str'] = 'str'
        self.section['ep_int'] = 23
        self.section['ep_float'] = 42.0
        self.section['ep_list'] = [1, 2, 3]
        self.section['ep_val'] = 1.0

        self.section['ep_val'] = 2.0

        # prop creation through create_property
        self.section.create_property('cp_str', 'str')
        self.section.create_property('cp_int', 23)
        self.section.create_property('cp_float', 42.0)
        self.section.create_property('cp_list', [1, 2, 3])
        self.section.create_property('cp_val', 1.0)

        self.section.props["cp_str"].values = "anotherstr"

        res = [x in self.section for x in ['ep_str', 'ep_int', 'ep_float']]
        assert all(res)

        assert self.section['ep_str'] == 'str'
        assert self.section['ep_int'] == 23
        assert self.section['ep_float'] == 42.0
        assert self.section['ep_list'] == [1, 2, 3]

        def create_hetero_section():
            self.section['ep_ex'] = [1, 1.0]

        self.assertRaises(TypeError, create_hetero_section)

        sections = [x.id for x in self.section]
        for x in sections:
            del self.section[x]

        assert len(self.section) == 0

    def test_parent(self):
        self.assertIs(self.section.parent, None)
        child = self.section.create_section("child section", "sect")
        self.assertEqual(self.section, child.parent)

        block = self.file.create_block("block", "section parent test")
        mdsection = self.file.create_section("block md", "metadata sect")
        block.metadata = mdsection
        self.assertIs(block.metadata.parent, None)

        grp = block.create_group("group", "section parent test")
        grp.metadata = child
        self.assertEqual(grp.metadata.parent, self.section)

        # indirect access parent check
        self.assertEqual(block.groups["group"].metadata.parent, self.section)

    def test_inverse_search(self):
        block = self.file.create_block("a block", "block with metadata")
        block.metadata = self.section

        otherblock = self.file.create_block("b block", "block with metadata")
        otherblock.metadata = self.other

        self.file.create_block("c block", "block without metadata")

        self.assertEqual(len(self.section.referring_blocks), 1)
        self.assertEqual(len(self.other.referring_blocks), 1)
        self.assertEqual(self.section.referring_blocks[0], block)
        self.assertEqual(self.other.referring_blocks[0], otherblock)

        da_one = block.create_data_array("foo", "data_array", data=range(10))
        da_one.metadata = self.other
        da_two = block.create_data_array("foobar", "data_array", data=[1])
        da_two.metadata = self.other

        block.create_data_array("nomd", "data_array", data=[9])

        self.assertEqual(len(self.other.referring_data_arrays), 2)
        self.assertIn(da_one, self.other.referring_data_arrays)
        self.assertIn(da_two, self.other.referring_data_arrays)

        tag = block.create_tag("tago", "tagtype", [1, 1])
        tag.metadata = self.section

        block.create_tag("tagi", "tagtype", [1, 10])
        self.assertEqual(len(self.section.referring_tags), 1)
        self.assertEqual(len(self.other.referring_tags), 0)
        self.assertEqual(self.section.referring_tags[0].id, tag.id)

        mtag = block.create_multi_tag("MultiTagName", "MultiTagType", da_one)
        mtag.metadata = self.section
        block.create_multi_tag("MtagNOMD", "MultiTagType", da_one)
        self.assertEqual(len(self.section.referring_multi_tags), 1)
        self.assertEqual(len(self.other.referring_multi_tags), 0)
        self.assertEqual(self.section.referring_multi_tags[0].id, mtag.id)

        src = block.create_source("sauce", "stype")
        src.metadata = self.other
        block.create_source("nosauce", "stype")
        self.assertEqual(len(self.other.referring_sources), 1)
        self.assertEqual(len(self.section.referring_sources), 0)
        self.assertEqual(self.other.referring_sources[0].id, src.id)

    def test_section_link(self):
        self.section.create_property("PropOnSection", "value")

        self.assertIn("PropOnSection", self.section)
        self.assertEqual("value", self.section["PropOnSection"])

        self.assertNotIn("PropOnSection", self.other)
        with self.assertRaises(KeyError):
            self.other["PropOnSection"]

        self.other.link = self.section

        self.assertNotIn("PropOnSection", self.other)
        with self.assertRaises(KeyError):
            self.other["PropOnSection"]

        inhpropnames = [p.name for p in self.other.inherited_properties()]
        self.assertIn("PropOnSection", inhpropnames)

    # Test for copying props and sections on sections
    def test_copy_on_sections(self):
        tarfilename = os.path.join(self.tmpdir.path, "destination.nix")
        tarfile = nix.File.open(tarfilename, nix.FileMode.Overwrite)
        sec1 = self.section
        prop1 = sec1.create_property("prop from origin",
                                     values_or_dtype=[1, 2, 3])
        sec2 = sec1.create_section("nested sec", 'test nested')
        tarsec = tarfile.create_section("tar sec", "tar")
        tarsec.create_property(copy_from=prop1)
        assert prop1 == tarsec.props[0]
        tarsec.copy_section(sec1)
        tarsec.copy_section(sec2)
        assert sec1 == tarsec.sections[0]
        assert sec2 == tarsec.sections[1]
        assert sec1.sections[0] == tarsec.sections[1]
        tarfile.close()

    def test_timestamp_autoupdate(self):
        section = self.file.create_section("section.time", "test.time")

        sectime = section.updated_at
        time.sleep(1)  # wait for time to change
        section.reference = "whatever"
        self.assertNotEqual(sectime, section.updated_at)

        sectime = section.updated_at
        linksec = self.file.create_section("link.section.time", "test.time")
        time.sleep(1)  # wait for time to change
        section.link = linksec
        self.assertNotEqual(sectime, section.updated_at)

        sectime = section.updated_at
        time.sleep(1)  # wait for time to change
        section.repository = "repo"
        self.assertNotEqual(sectime, section.updated_at)

    def test_timestamp_noautoupdate(self):
        self.file.auto_update_timestamps = False
        section = self.file.create_section("section.time", "test.time")

        sectime = section.updated_at
        time.sleep(1)  # wait for time to change
        section.reference = "whatever"
        self.assertEqual(sectime, section.updated_at)

        sectime = section.updated_at
        time.sleep(1)  # wait for time to change
        linksec = self.file.create_section("link.section.time", "test.time")
        section.link = linksec
        self.assertEqual(sectime, section.updated_at)

        sectime = section.updated_at
        time.sleep(1)  # wait for time to change
        section.repository = "repo"
        self.assertEqual(sectime, section.updated_at)
