# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

import unittest

from nixio import *
try:
    import nixio.core
    skip_cpp = False
except ImportError:
    skip_cpp = True
import nixio


class _TestSection(unittest.TestCase):

    def tearDown(self):
        del self.file.sections[self.section.id]
        del self.file.sections[self.other.id]
        self.file.close()

    def test_section_eq(self):
        assert(self.section == self.section)
        assert(not self.section == self.other)
        assert(not self.section == None)

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

        assert(child      in self.section.sections)
        assert(child.id   in self.section.sections)
        assert("notexist" not in self.section.sections)

        assert(child.id == self.section.sections[0].id)
        assert(child.id == self.section.sections[-1].id)

        del self.section.sections[0]

        assert(len(self.section.sections) == 0)

        self.section['easy subsection'] = nixio.S('electrode')
        subject = self.section['subject'] = nixio.S('subject')
        
        assert(self.section['subject'] == subject)
        assert(self.section['subject'].id == subject.id)
        assert('easy subsection' in [v.name for k, v in self.section.sections.items()])
        assert('easy subsection' in self.section.sections)
        assert(self.section['easy subsection'].name == 'easy subsection')
        #assert('easy subsection' in self.section)

    def test_section_find_sections(self):
        for i in range(2): self.section.create_section("level1-p0-s" + str(i), "dummy")
        for i in range(2): self.section.sections[0].create_section("level2-p1-s" + str(i), "dummy")
        for i in range(2): self.section.sections[1].create_section("level2-p2-s" + str(i), "dummy")
        for i in range(2): self.section.sections[0].sections[0].create_section("level3-p1-s" + str(i), "dummy")

        assert(len(self.section.find_sections()) == 9)
        assert(len(self.section.find_sections(limit=1)) == 3)
        assert(len(self.section.find_sections(filtr=lambda x : "level2-p1-s" in x.name)) == 2)
        assert(len(self.section.find_sections(filtr=lambda x : "level2-p1-s" in x.name, limit=1)) == 0)

        assert(len(self.section.find_related()) == 3)
        assert(len(self.section.sections[0].find_related()) == 5)

    def test_section_properties(self):
        assert(len(self.section) == 0)

        prop = self.section.create_property("test prop", DataType.String)

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

        #easy prop creation
        self.section['ep_str'] = 'str'
        self.section['ep_int'] = 23
        self.section['ep_float'] = 42.0
        self.section['ep_list'] = [1, 2, 3]
        self.section['ep_val'] = Value(1.0)

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


@unittest.skipIf(skip_cpp, "HDF5 backend not available.")
class TestSectionCPP(_TestSection):

    def setUp(self):
        self.file    = File.open("unittest.h5", FileMode.Overwrite,
                                 backend="hdf5")
        self.section = self.file.create_section("test section", "recordingsession")
        self.other   = self.file.create_section("other section", "recordingsession")


class TestSectionPy(_TestSection):

    def setUp(self):
        self.file = File.open("unittest.h5", FileMode.Overwrite, backend="h5py")

    def tearDown(self):
        pass

    def test_section_eq(self):
        pass

    def test_section_id(self):
        pass

    def test_section_name(self):
        pass

    def test_section_type(self):
        pass

    def test_section_definition(self):
        pass

    def test_section_mapping(self):
        pass

    def test_section_repository(self):
        pass

    def test_section_sections(self):
        pass

    def test_section_find_sections(self):
        pass

    def test_section_properties(self):
        pass
