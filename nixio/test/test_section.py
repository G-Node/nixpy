# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)
import nixio as nix
import unittest



class TestSection(unittest.TestCase):

    def setUp(self):
        self.file = nix.File.open("unittest.h5", nix.FileMode.Overwrite)
        self.section = self.file.create_section("test section",
                                                "recordingsession")
        self.other = self.file.create_section("other section",
                                              "recordingsession")

    def tearDown(self):
        del self.file.sections[self.section.id]
        del self.file.sections[self.other.id]
        self.file.close()
        os.remove(self.testfilename)

    def test_section_eq(self):
        assert(self.section == self.section)
        assert(not self.section == self.other)
        assert(self.section is not None)

    def test_section_id(self):
        assert(self.section.id is not None)

    def test_section_name(self):
        assert(self.section.name is not None)

    def test_section_type(self):
        def set_none():
            self.section.type = None

        assert(self.section.type is not None)
        self.assertRaises(Exception, set_none)

        self.section.type = "foo type"
        assert(self.section.type == "foo type")

    def test_section_definition(self):
        assert(self.section.definition is None)

        self.section.definition = "definition"
        assert(self.section.definition == "definition")

        self.section.definition = None
        assert(self.section.definition is None)

    def test_section_mapping(self):
        assert(self.section.mapping is None)

        self.section.mapping = "mapping"
        assert(self.section.mapping == "mapping")

        self.section.mapping = None
        assert(self.section.mapping is None)

    def test_section_repository(self):
        assert(self.section.repository is None)

        self.section.repository = "repository"
        assert(self.section.repository == "repository")

        self.section.repository = None
        assert(self.section.repository is None)

    def test_section_sections(self):
        assert(len(self.section.sections) == 0)

        child = self.section.create_section("test section", "electrode")
        assert(child.parent == self.section)

        assert(len(self.section.sections) == 1)

        assert(child in self.section.sections)
        assert(child.id in self.section.sections)
        assert("notexist" not in self.section.sections)

        assert(child.id == self.section.sections[0].id)
        assert(child.id == self.section.sections[-1].id)

        del self.section.sections[0]

        assert(len(self.section.sections) == 0)

        self.section['easy subsection'] = nix.S('electrode')
        subject = self.section['subject'] = nix.S('subject')

        assert(self.section['subject'] == subject)
        assert(self.section['subject'].id == subject.id)
        assert('easy subsection' in
               [v.name for k, v in self.section.sections.items()])
        assert('easy subsection' in self.section.sections)
        assert(self.section['easy subsection'].name == 'easy subsection')

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

        assert(len(self.section.find_sections()) == 9)
        assert(len(self.section.find_sections(limit=1)) == 3)
        assert(len(self.section.find_sections(
            filtr=lambda x: "level2-p1-s" in x.name)) == 2
               )
        assert(len(self.section.find_sections(
            filtr=lambda x: "level2-p1-s" in x.name, limit=1)) == 0
               )

        assert(len(self.section.find_related()) == 3)
        assert(len(self.section.sections[0].find_related()) == 5)

    def test_section_properties(self):
        assert(len(self.section) == 0)

        prop = self.section.create_property("test prop", nix.DataType.String)

        assert(len(self.section) == 1)

        for p in self.section:
            assert(p in self.section)

        assert(self.section.has_property_by_name("test prop"))
        assert(not self.section.has_property_by_name("notexist"))
        assert(self.section.get_property_by_name("test prop") is not None)
        assert(self.section.get_property_by_name("notexist") is None)

        assert(len(self.section.inherited_properties()) == 1)

        assert(prop in self.section)
        assert(prop.id in self.section)
        assert(prop.name in self.section)
        assert("notexist" not in self.section)

        props = dict(self.section.items())
        assert(props["test prop"] == prop)

        assert(prop.id == self.section.props[0].id)
        assert(prop.id == self.section.props[-1].id)

        # easy prop creation
        self.section['ep_str'] = 'str'
        self.section['ep_int'] = 23
        self.section['ep_float'] = 42.0
        self.section['ep_list'] = [1, 2, 3]
        self.section['ep_val'] = nix.Value(1.0)

        self.section['ep_val'] = 2.0

        res = [x in self.section for x in ['ep_str', 'ep_int', 'ep_float']]
        assert(all(res))

        assert(self.section['ep_str'] == 'str')
        assert(self.section['ep_int'] == 23)
        assert(self.section['ep_float'] == 42.0)
        assert(self.section['ep_list'] == [1, 2, 3])

        def create_hetero_section():
            self.section['ep_ex'] = [1, 1.0]
        self.assertRaises(ValueError, create_hetero_section)

        sections = [x.id for x in self.section]
        for x in sections:
            del self.section[x]

        assert(len(self.section) == 0)

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

    def test_inverse_search(self):
        block = self.file.create_block("a block", "block with metadata")
        block.metadata = self.section

        otherblock = self.file.create_block("b block", "block with metadata")
        otherblock.metadata = self.other

        self.assertEqual(len(self.section.referring_blocks), 1)
        self.assertEqual(len(self.other.referring_blocks), 1)
        self.assertEqual(self.section.referring_blocks[0], block)
        self.assertEqual(self.other.referring_blocks[0], otherblock)

        da_one = block.create_data_array("foo", "data_array", data=range(10))
        da_one.metadata = self.other
        da_two = block.create_data_array("foobar", "data_array", data=[1])
        da_two.metadata = self.other

        self.assertEqual(len(self.other.referring_data_arrays), 2)
        self.assertIn(da_one, self.other.referring_data_arrays)
        self.assertIn(da_two, self.other.referring_data_arrays)

        tag = block.create_tag("tago", "tagtype", [1, 1])
        tag.metadata = self.section
        self.assertEqual(len(self.section.referring_tags), 1)
        self.assertEqual(len(self.other.referring_tags), 0)
        self.assertEqual(self.section.referring_tags[0].id, tag.id)

        mtag = block.create_multi_tag("MultiTagName", "MultiTagType", da_one)
        mtag.metadata = self.section
        self.assertEqual(len(self.section.referring_multi_tags), 1)
        self.assertEqual(len(self.other.referring_multi_tags), 0)
        self.assertEqual(self.section.referring_multi_tags[0].id, mtag.id)

        src = block.create_source("sauce", "stype")
        src.metadata = self.other
        self.assertEqual(len(self.other.referring_sources), 1)
        self.assertEqual(len(self.section.referring_sources), 0)
        self.assertEqual(self.other.referring_sources[0].id, src.id)
