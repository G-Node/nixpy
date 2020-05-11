# -*- coding: utf-8 -*-
# Copyright © 2017, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import os
import random
import nixio as nix
import unittest
from .tmp import TempDir


class TestContainer(unittest.TestCase):

    def setUp(self):
        self.tmpdir = TempDir("containertest")
        self.testfilename = os.path.join(self.tmpdir.path, "containertest.nix")
        self.file = nix.File.open(self.testfilename, nix.FileMode.Overwrite)
        self.block = self.file.create_block("test block", "containertest")
        self.dataarray = self.block.create_data_array("test array",
                                                      "containertest",
                                                      data=[0])
        self.tag = self.block.create_tag("test tag", "containertest",
                                         position=[1.9, 20])
        self.positions = self.block.create_data_array("test pos",
                                                      "containertest",
                                                      data=[1])
        self.multi_tag = self.block.create_multi_tag("test multitag",
                                                     "containertest",
                                                     positions=self.positions)
        self.group = self.block.create_group("test group",
                                             "containertest")

        self.group.data_arrays.append(self.dataarray)
        self.group.tags.append(self.tag)
        self.group.multi_tags.append(self.multi_tag)

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()
        self.tmpdir.cleanup()

    def test_name_getter(self):
        self.assertEqual(self.block, self.file.blocks["test block"])
        self.assertEqual(self.dataarray, self.block.data_arrays["test array"])
        self.assertEqual(self.tag, self.block.tags["test tag"])
        self.assertEqual(self.multi_tag,
                         self.block.multi_tags["test multitag"])
        self.assertEqual(self.group, self.block.groups["test group"])
        self.assertEqual(self.positions, self.block.data_arrays["test pos"])

    def test_index_getter(self):
        self.assertEqual(self.block, self.file.blocks[0])
        self.assertEqual(self.dataarray, self.block.data_arrays[0])
        self.assertEqual(self.tag, self.block.tags[0])
        self.assertEqual(self.multi_tag,
                         self.block.multi_tags[0])
        self.assertEqual(self.group, self.block.groups[0])
        self.assertEqual(self.positions, self.block.data_arrays[1])

    def test_link_container_name_getter(self):
        self.assertEqual(self.dataarray, self.group.data_arrays["test array"])
        self.assertEqual(self.tag, self.group.tags["test tag"])
        self.assertEqual(self.multi_tag,
                         self.group.multi_tags["test multitag"])

    def test_link_container_index_getter(self):
        self.assertEqual(self.dataarray, self.group.data_arrays[0])
        self.assertEqual(self.tag, self.group.tags[0])
        self.assertEqual(self.multi_tag,
                         self.group.multi_tags[0])

    def test_file_references(self):
        # add some sources
        self.source = self.block.create_source("test source", "containertest")
        self.child_source = self.source.create_source("test source 2",
                                                      "containertest")
        # using assertIs since the reference should be the same instance as
        # the original

        # created objects
        self.assertIs(self.block.file, self.file)
        self.assertIs(self.group.file, self.file)
        self.assertIs(self.dataarray.file, self.file)
        self.assertIs(self.tag.file, self.file)
        self.assertIs(self.multi_tag.file, self.file)
        self.assertIs(self.positions.file, self.file)
        self.assertIs(self.source.file, self.file)
        self.assertIs(self.child_source.file, self.file)

        # instantiated through container getters
        blk = self.file.blocks[0]
        self.assertIs(blk.file, self.file)
        self.assertIs(blk.groups[0].file, self.file)
        self.assertIs(blk.data_arrays[0].file, self.file)
        self.assertIs(blk.tags[0].file, self.file)
        self.assertIs(blk.multi_tags[0].file, self.file)
        self.assertIs(blk.sources[0].file, self.file)
        self.assertIs(blk.sources[0].sources[0].file, self.file)

        # linked through group
        self.assertIs(self.group.data_arrays[0].file, self.file)
        self.assertIs(self.group.tags[0].file, self.file)
        self.assertIs(self.group.multi_tags[0].file, self.file)

    def test_parent_references(self):
        # add some sources
        self.source = self.block.create_source("test source", "containertest")
        self.child_source = self.source.create_source("test source 2",
                                                      "containertest")

        self.assertEqual(self.block._parent, self.file)
        self.assertEqual(self.group._parent, self.block)
        self.assertEqual(self.dataarray._parent, self.block)
        self.assertEqual(self.tag._parent, self.block)
        self.assertEqual(self.multi_tag._parent, self.block)
        self.assertEqual(self.positions._parent, self.block)
        self.assertEqual(self.source._parent, self.block)
        self.assertEqual(self.child_source._parent, self.source)

    def test_link_parent_references(self):
        self.assertEqual(self.group.data_arrays[0]._parent, self.block)
        self.assertEqual(self.group.tags[0]._parent, self.block)
        self.assertEqual(self.group.multi_tags[0]._parent, self.block)

    def test_bad_appends(self):
        # use fresh file for this one
        filename = os.path.join(self.tmpdir.path, "badappend.nix")
        nf = nix.File.open(filename, nix.FileMode.Overwrite)

        for blockname in ["a", "b"]:
            block = nf.create_block(blockname, "block")

            for groupname in ["a", "b"]:
                group = block.create_group(blockname + groupname, "group")
                for daname in ["a", "b"]:
                    da = block.create_data_array(
                        blockname + groupname + daname, "data", data=[0]
                    )
                    group.data_arrays.append(da)
                    tag = block.create_tag(
                        blockname + groupname + daname, "tag", position=[0]
                    )
                    group.tags.append(tag)

        # check counts
        self.assertEqual(len(nf.blocks), 2)
        for bl in nf.blocks:
            self.assertEqual(len(bl.groups), 2)
            self.assertEqual(len(bl.data_arrays), 4)
            self.assertEqual(len(bl.tags), 4)
            for g in bl.groups:
                self.assertEqual(len(g.data_arrays), 2)
                self.assertEqual(len(g.tags), 2)

        # cross-block append
        with self.assertRaises(RuntimeError):
            nf.blocks[0].groups[0].data_arrays.append(
                nf.blocks[1].data_arrays[1]
            )

        # another
        with self.assertRaises(RuntimeError):
            nf.blocks[1].groups[0].tags.append(
                nf.blocks[0].tags[1]
            )

        # append data array to group.tags
        with self.assertRaises(TypeError):
            nf.blocks[0].groups[0].tags.append(
                nf.blocks[0].data_arrays[2]
            )

        # cross-block *and* incorrect type
        with self.assertRaises(TypeError):
            nf.blocks[0].groups[0].tags.append(
                nf.blocks[1].data_arrays[2]
            )

        # let's do sources
        for bl in nf.blocks:
            for sourcename in ["a", "b"]:
                src = bl.create_source(bl.name + sourcename, "source")
                for chsourcename in ["a", "b", "c"]:
                    src.create_source(bl.name + sourcename + chsourcename,
                                      "source")

        # check counts
        for bl in nf.blocks:
            self.assertEqual(len(bl.sources), 2)
            for src in bl.sources:
                self.assertEqual(len(src.sources), 3)

        # cross-block source append
        with self.assertRaises(RuntimeError):
            nf.blocks[1].groups[0].sources.append(
                nf.blocks[0].sources[1]
            )

        # cross-block source append (deep)
        with self.assertRaises(RuntimeError):
            nf.blocks[1].groups[0].sources.append(
                nf.blocks[0].sources[1].sources[2]
            )

        # valid deep append
        nf.blocks[0].groups[0].data_arrays[1].sources.append(
            nf.blocks[0].sources[1].sources[2]
        )

        # bad membership test
        with self.assertRaises(TypeError):
            nf.blocks[1].data_arrays[1] in nf.blocks[0].tags

        # another
        with self.assertRaises(TypeError):
            nf.blocks[1].data_arrays[1] in nf.blocks[0].groups[0]

        # bad membership test on LinkContainer
        with self.assertRaises(TypeError):
            nf.blocks[1].data_arrays[1] in nf.blocks[0].groups[0].tags

    def test_delete_links_da(self):
        # delete DataArray from Block and check Group
        daname = "new-data-array"
        da = self.block.create_data_array(daname, "to-be-deleted", data=[0])
        self.block.groups[0].data_arrays.append(da)
        self.assertIn(self.block.data_arrays[-1],
                      self.block.groups[-1].data_arrays)
        self.assertIn(daname, self.block.groups[0].data_arrays)

        self.assertEqual(self.block.groups[-1].data_arrays[-1].name,
                         daname)

        del self.block.data_arrays[daname]
        self.assertNotIn(daname, self.block.data_arrays)
        self.assertNotIn(daname, self.block.groups[0].data_arrays)

    def test_delete_links_tag(self):
        # delete Tag from Block and check Group
        tagname = "new-tag"
        tag = self.block.create_tag(tagname, "to-be-deleted", position=[0])
        self.block.groups[0].tags.append(tag)
        self.assertIn(self.block.tags[-1],
                      self.block.groups[-1].tags)
        self.assertIn(tagname, self.block.groups[0].tags)

        self.assertEqual(self.block.groups[-1].tags[-1].name, tagname)

        del self.block.tags[tagname]
        self.assertNotIn(tagname, self.block.tags)
        self.assertNotIn(tagname, self.block.groups[0].tags)

    def test_delete_links_multitag(self):
        # delete MultiTag DataArrays and check positions and extents
        posname = "new-mt-positions"
        pos = self.block.create_data_array(posname, "to-be-deleted", data=[0])
        extname = "new-mt-extents"
        ext = self.block.create_data_array(extname, "to-be-deleted", data=[0])

        mtagname = "new-multi-tag"
        mtag = self.block.create_multi_tag(mtagname, "to-be-deleted",
                                           positions=pos)
        mtag.extents = ext
        self.block.groups[0].multi_tags.append(mtag)

        self.assertEqual(mtag.positions, pos)
        del self.block.data_arrays[posname]
        with self.assertRaises(RuntimeError):
            mtag.positions
        # ext still here
        self.assertEqual(mtag.extents, ext)
        # delete ext and check extents
        del self.block.data_arrays[extname]
        self.assertIsNone(mtag.extents)

        # delete MultiTag and check Group
        self.assertIn(mtagname, self.block.multi_tags)
        self.assertIn(mtag.id, self.block.multi_tags)
        self.assertIn(mtag, self.block.multi_tags)
        del self.block.multi_tags[mtagname]
        self.assertNotIn(mtagname, self.block.multi_tags)

    def test_delete_links_references(self):
        posname = "new-mt-positions"
        pos = self.block.create_data_array(posname, "to-be-deleted", data=[0])

        tagname = "new-tag"
        tag = self.block.create_tag(tagname, "to-be-deleted",
                                    position=[1, 3, 10])
        self.block.groups[0].tags.append(tag)

        mtagname = "new-multi-tag"
        mtag = self.block.create_multi_tag(mtagname, "to-be-deleted",
                                           positions=pos)
        self.block.groups[0].multi_tags.append(mtag)

        refnamea = "new-da-ref-a"
        refa = self.block.create_data_array(refnamea, "to-be-deleted",
                                            data=[10])
        tag.references.append(refa)
        mtag.references.append(refa)

        refnameb = "new-da-ref-b"
        refb = self.block.create_data_array(refnameb, "to-be-deleted",
                                            data=[11])
        tag.references.append(refb)
        mtag.references.append(refb)

        # delete ref DAs and check refs
        del self.block.data_arrays[refnamea]
        self.assertNotIn(refnamea, tag.references)
        self.assertIn(refnameb, tag.references)
        self.assertNotIn(refnamea, mtag.references)
        self.assertIn(refnameb, mtag.references)

        del self.block.data_arrays[refnameb]
        self.assertNotIn(refnameb, tag.references)
        self.assertNotIn(refnameb, mtag.references)

    def test_delete_links_sources(self):
        sourcetreedepth = 5

        # make a random source tree
        def make_sources(par, depth=0):
            if depth == sourcetreedepth:
                return
            for srcidx in range(3):
                srcname = "{}:src-{}".format(par.name, srcidx)
                srctype = "Source at depth {}".format(depth)
                chsrc = par.create_source(srcname, srctype)
                make_sources(chsrc, depth+1)

        make_sources(self.block)

        def get_rand_src(par, depth=None):
            if depth is None:
                depth = random.randint(0, sourcetreedepth-1)

            idx = random.randint(0, len(par.sources)-1)
            chsrc = par.sources[idx]
            if depth == 0:
                return chsrc

            return get_rand_src(chsrc, depth-1)

        # link a couple of random sources to dataarray
        parenta = get_rand_src(self.block, depth=3)
        sourcea = parenta.sources[-1]
        self.dataarray.sources.append(sourcea)

        parentb = get_rand_src(self.block, depth=2)
        sourceb = parentb.sources[0]
        self.dataarray.sources.append(sourceb)

        # delete sourcea from parent
        namelsa = sourcea.name
        del parenta.sources[namelsa]
        # check references
        self.assertNotIn(namelsa, parenta.sources)
        self.assertNotIn(namelsa, self.dataarray.sources)
        self.assertIn(sourceb, self.dataarray.sources)

        # delete sourceb from parent
        namelsb = sourceb.name
        del parentb.sources[namelsb]
        # check references
        self.assertNotIn(namelsb, parentb.sources)
        self.assertNotIn(sourceb, self.dataarray.sources)

        # link a deep source and delete its parent
        grandparentc = get_rand_src(self.block, depth=0)
        parentc = get_rand_src(grandparentc, depth=0)
        sourcec = get_rand_src(parentc, depth=0)
        self.tag.sources.append(sourcec)
        cname = sourcec.name
        del grandparentc.sources[parentc.name]
        self.assertNotIn(cname, self.tag.sources)

    def test_delete_links_sections(self):
        sectiontreedepth = 5

        rootsec = self.file.create_section("GOD", "I AM THE TOP SECTION")

        # make a random section tree
        def make_sections(par, depth=0):
            if depth == sectiontreedepth:
                return
            for secidx in range(3):
                secname = "{}:sec-{}".format(par.name, secidx)
                sectype = "section at depth {}".format(depth)
                chsec = par.create_section(secname, sectype)
                make_sections(chsec, depth+1)

        make_sections(rootsec)

        def get_rand_sec(par, depth=None):
            if depth is None:
                depth = random.randint(0, sectiontreedepth-1)

            idx = random.randint(0, len(par.sections)-1)
            chsec = par.sections[idx]
            if depth == 0:
                return chsec

            return get_rand_sec(chsec, depth-1)

        # link a couple of random sections to dataarray
        parenta = get_rand_sec(rootsec, depth=3)
        sectiona = parenta.sections[-1]
        self.dataarray.metadata = sectiona

        parentb = get_rand_sec(rootsec, depth=2)
        sectionb = parentb.sections[0]
        self.multi_tag.metadata = sectionb

        # delete sectiona from parent
        namelsa = sectiona.name
        del parenta.sections[namelsa]
        # check references
        self.assertNotIn(namelsa, parenta.sections)
        self.assertIsNone(self.dataarray.metadata)
        self.assertEqual(sectionb, self.multi_tag.metadata)

        # delete sectionb from parent
        namelsb = sectionb.name
        del parentb.sections[namelsb]
        # check references
        self.assertNotIn(namelsb, parentb.sections)
        self.assertIsNone(self.multi_tag.metadata)

        # link a deep section and delete its parent
        grandparentc = get_rand_sec(rootsec, depth=0)
        parentc = get_rand_sec(grandparentc, depth=0)
        sectionc = get_rand_sec(parentc, depth=0)
        self.tag.metadata = sectionc
        del grandparentc.sections[parentc.name]
        self.assertIsNone(self.tag.metadata)

    def test_delete_links_tag_features(self):
        posname = "new-mt-positions"
        pos = self.block.create_data_array(posname, "to-be-deleted", data=[0])

        tagname = "new-tag"
        tag = self.block.create_tag(tagname, "to-be-deleted",
                                    position=[1, 3, 10])
        self.block.groups[0].tags.append(tag)

        mtagname = "new-multi-tag"
        mtag = self.block.create_multi_tag(mtagname, "to-be-deleted",
                                           positions=pos)
        self.block.groups[0].multi_tags.append(mtag)

        dataname = "new-da-feat-a"
        feat_da = self.block.create_data_array(dataname, "to-be-deleted",
                                               data=[10])

        tag.create_feature(feat_da, nix.LinkType.Indexed)

        self.assertIn(dataname, self.block.data_arrays)
        self.assertIn(dataname, tag.features)

        del self.block.data_arrays[dataname]

        self.assertNotIn(dataname, self.block.data_arrays)

        with self.assertRaises(RuntimeError):
            self.assertNotIn(dataname, tag.features)

        with self.assertRaises(RuntimeError):
            tag.features[dataname].data

    def test_delete_links_section_link(self):
        parsec = self.file.create_section("TopDog", "Root Section")
        chsec = parsec.create_section("1Dog", "Level 1 section")
        chchsec = chsec.create_section("2Dog", "Level 2 section")
        chchchsec = chchsec.create_section("3Dog", "Level 3 section")

        chchsec.create_property("2Prop", "Level 2 property")
        chchchsec.create_property("3Prop", "Level 3 property")

        chsecb = parsec.create_section("1Dog2", "Level 1 section")

        # link chchchsec to chsecb and then delete it
        chsecb.link = chchchsec

        inhpropnames = [p.name for p in chsecb.inherited_properties()]
        self.assertEqual(chchchsec, chsecb.link)
        self.assertIn("3Prop", inhpropnames)

        # delete chchchsec and check link and inherited props
        del chchsec.sections["3Dog"]
        inhpropnames = [p.name for p in chsecb.inherited_properties()]
        self.assertIs(None, chsecb.link)
        self.assertNotIn("3Prop", inhpropnames)

        # link chchsec to chsecb then delete chsec (chchsec's parent)
        chsecb.link = chchsec

        inhpropnames = [p.name for p in chsecb.inherited_properties()]
        self.assertEqual(chchsec, chsecb.link)
        self.assertIn("2Prop", inhpropnames)

        # delete chsec and check link and inherited props
        del parsec.sections["1Dog"]
        inhpropnames = [p.name for p in chsecb.inherited_properties()]
        self.assertIs(None, chsecb.link)
        self.assertNotIn("2Prop", inhpropnames)
