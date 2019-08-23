# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import annotations
import os
import gc
import numpy as np
from warnings import warn

try:
    from sys import maxint
except ImportError:
    from sys import maxsize as maxint
import h5py

from .hdf5.h5group import H5Group
from .block import Block
from .section import Section
from .container import Container, SectionContainer
from . import util
from .exceptions import InvalidFile, DuplicateName
from .util import find as finders
from .validate import Validate
from .compression import Compression
from .dimensions import RangeDimension, SetDimension, SampledDimension
from typing import AnyStr, List, Optional, Union


FILE_FORMAT = "nix"
HDF_FF_VERSION = (1, 1, 1)


def can_write(nixfile) -> bool:
    filever = nixfile.version
    if len(filever) != 3:
        raise RuntimeError("Invalid version specified in file.")
    if HDF_FF_VERSION == filever:
        return True
    else:
        return False


def can_read(nixfile) -> bool:
    filever = nixfile.version
    if len(filever) != 3:
        raise RuntimeError("Invalid version specified in file.")
    vx, vy, vz = HDF_FF_VERSION
    fx, fy, fz = filever
    if vx == fx and vy >= fy:
        return True
    else:
        return False


class FileMode(object):
    ReadOnly = 'r'
    ReadWrite = 'a'
    Overwrite = 'w'



def map_file_mode(mode) -> int:
    if mode == FileMode.ReadOnly:
        return h5py.h5f.ACC_RDONLY
    elif mode == FileMode.ReadWrite:
        return h5py.h5f.ACC_RDWR
    elif mode == FileMode.Overwrite:
        return h5py.h5f.ACC_TRUNC
    else:
        raise ValueError("Invalid file mode specified.")


def make_fapl():
    return h5py.h5p.create(h5py.h5p.FILE_ACCESS)


def make_fcpl():
    fcpl = h5py.h5p.create(h5py.h5p.FILE_CREATE)
    flags = h5py.h5p.CRT_ORDER_TRACKED | h5py.h5p.CRT_ORDER_INDEXED
    fcpl.set_link_creation_order(flags)
    return fcpl


class File(object):

    def __init__(self, path, mode=FileMode.ReadWrite,
                 compression=Compression.Auto, auto_update_time=False) -> None:
        """
        Open a NIX file, or create it if it does not exist.

        :param path: Path to file
        :param mode: FileMode ReadOnly, ReadWrite, or Overwrite.
                    (default: ReadWrite)
        :param compression: No, DeflateNormal, Auto (default: Auto)
        :return: nixio.File object
        """
        try:
            path = path.encode("utf-8")
        except (UnicodeError, LookupError):
            pass

        if not os.path.exists(path) and mode == FileMode.ReadOnly:
            raise RuntimeError(
                "Cannot open non-existent file in ReadOnly mode!"
            )

        new = False
        if not os.path.exists(path) or mode == FileMode.Overwrite:
            mode = FileMode.Overwrite
            h5mode = map_file_mode(mode)
            fid = h5py.h5f.create(path, flags=h5mode, fapl=make_fapl(),
                                  fcpl=make_fcpl())
            new = True
        else:
            h5mode = map_file_mode(mode)
            fid = h5py.h5f.open(path, flags=h5mode, fapl=make_fapl())

        self._h5file = h5py.File(fid)
        self._root = H5Group(self._h5file, "/", create=True)
        self._h5group = self._root  # to match behaviour of other objects
        self._time_auto_update = True
        if new:
            self._create_header()
        self._check_header(mode)
        self.mode = mode
        self._data = self._root.open_group("data", create=True)
        self.metadata = self._root.open_group("metadata", create=True)
        if "created_at" not in self._h5file.attrs:
            self.force_created_at()
        if "updated_at" not in self._h5file.attrs:
            self.force_updated_at()
        self.time_auto_update = auto_update_time
        if compression == Compression.Auto:
            compression = Compression.No
        self._compr = compression
        # make container props but don't initialise
        self._blocks = None
        self._sections = None

    @classmethod
    def open(cls, path, mode=FileMode.ReadWrite, compression=Compression.Auto,
             backend=None,  auto_update_time=False) -> File:
        if backend is not None:
            warn("Backend selection is deprecated. Ignoring value.")
        return cls(path, mode, compression, auto_update_time)

    def _create_header(self) -> None:
        self.format = FILE_FORMAT
        self.version = HDF_FF_VERSION

    def _check_header(self, mode) -> None:
        if self.format != FILE_FORMAT:
            raise InvalidFile

        if mode == FileMode.ReadWrite:
            if not can_write(self):
                raise RuntimeError("Cannot open file for writing. "
                                   "Incompatible version.")
        elif mode == FileMode.ReadOnly:
            if not can_read(self):
                raise RuntimeError("Cannot open file. "
                                   "Incompatible version.")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def version(self) -> tuple:
        """
        The file format version.

        :type: tuple
        """
        return tuple(self._root.get_attr("version"))

    @version.setter
    def version(self, v) -> None:
        util.check_attr_type(v, tuple)
        for part in v:
            util.check_attr_type(part, int)
        # convert to np.int32 since py3 defaults to 64
        v = np.array(v, dtype=np.int32)
        self._root.set_attr("version", v)
        if self.time_auto_update:
            self.force_updated_at()

    @property
    def format(self) -> AnyStr:
        """
        The format of the file. This read only property should always have the
        value 'nix'.

        :type: str
        """
        return self._root.get_attr("format")

    @format.setter
    def format(self, f) -> None:
        util.check_attr_type(f, str)
        self._root.set_attr("format", f.encode("ascii"))
        if self.time_auto_update:
            self.force_updated_at()

    @property
    def time_auto_update(self) -> bool:
        """
        A user defined flag which decided if time should always be updated
        when properties are changed.

        :type: bool
        """
        return self._time_auto_update

    @time_auto_update.setter
    def time_auto_update(self, auto_update_flag) -> None:
        self._time_auto_update = auto_update_flag

    @property
    def created_at(self) -> int:
        """
        The creation time of the file. This is a read-only property.
        Use `force_created_at` in order to change the creation time.

        :rtype: int
        """
        return util.str_to_time(self._h5file.attrs["created_at"])

    def force_created_at(self, t=None) -> None:
        """
        Sets the creation time `created_at` to the given time
        (default: current time).

        :param t: The time to set
        :type t: int
        """
        if t is None:
            t = util.now_int()
        else:
            util.check_attr_type(t, int)
        self._h5file.attrs["created_at"] = util.time_to_str(t)

    @property
    def updated_at(self) -> int:
        """
        The time of the last update of the file. This is a read-only
        property. Use `force_updated_at` in order to change the update
        time.

        :rtype: int
        """
        return util.str_to_time(self._h5file.attrs["updated_at"])

    def force_updated_at(self, t=None) -> None:
        """
        Sets the update time `updated_at` to the given time.
        (default: current time)

        :param t: The time to set (default: now)
        :type t: int
        """
        if t is None:
            t = util.now_int()
        else:
            util.check_attr_type(t, int)
        self._h5file.attrs["updated_at"] = util.time_to_str(t)

    def is_open(self) -> bool:
        """
        Checks whether a file is open or closed.

        :returns: True if the file is open, False otherwise.
        :rtype: bool
        """
        try:
            self._h5file.mode
            return True
        except ValueError:
            return False

    def validate(self) -> dict:
        """
        Checks if the file is a valid nix file.

        :returns: A dict which contains all objects in file and related errors
        :rtype: Dictionary
        """
        validator = Validate(self)
        validator.check_file()
        validator.form_dict()
        errors = validator.errors
        for bi, blk in enumerate(self.blocks):
            validator.check_blocks(blk, bi)
            for gi, grp in enumerate(blk.groups):
                validator.check_groups(grp, gi, bi)
            for di, da in enumerate(blk.data_arrays):
                validator.check_data_arrays(da, di, bi)
                for dimi, dim in enumerate(da.dimensions):
                    if isinstance(dim, RangeDimension):
                        validator.check_range_dim(dim, dimi, di, bi)
                    if isinstance(dim, SetDimension):
                        validator.check_set_dim(dim, dimi, di, bi)
                    if isinstance(dim, SampledDimension):
                        validator.check_sampled_dim(dim, dimi, di, bi)
            for mti, mt in enumerate(blk.multi_tags):
                validator.check_multi_tag(mt, mti, bi)
                for fi, fea in enumerate(mt.features):
                    validator.check_features(fea, 'multi_tags', bi, mti, fi)
            for ti, tag in enumerate(blk.tags):
                validator.check_tag(tag, ti, bi)
                for fi, fea in enumerate(tag.features):
                    validator.check_features(fea, 'tags', bi, ti, fi)
            for src in blk.find_sources():
                validator.check_sources(src, bi)

        for si, sec in enumerate(self.find_sections()):
            validator.check_section(sec, si)
            for pi, prop in enumerate(sec.props):
                validator.check_property(prop, pi, si)

        if validator.error_count:
            print("{} errors found".format(validator.error_count))
            return errors
        else:
            print("No errors found: The file is a valid NIX file")
            return errors

    def pprint(self, indent=2, max_length=120, extra=True, max_depth=3) -> None:
        """
        Pretty Printing the Data and MetaData Tree of the whole File

        :param indent: The length of one indentation space
        :type indent: int
        :param max_length: Maximum length of each line of output
        :type max_length: int
        :param extra: True to print extra information of Entities
        :type extra: bool
        :param max_depth: Maximum recursion being printed in MetaData tree
        :type max_depth: int
        """
        print("File: name = {}".format(self._h5group.group.file.filename))
        if self.blocks:
            for blk in self.blocks:
                blk.pprint(indent=indent,
                           max_length=max_length, extra=extra, start_depth=1)
        if self.sections:
            for sec in self.sections:
                sec.pprint(indent=indent, max_depth=max_depth,
                           max_length=max_length, current_depth=1)

    # TODO: if same file, set_attr("entity_id", id_)

    def copy_section(self, obj, children=True, keep_id=True, name="") -> Section:
        """
        Copy a section to the file.

        :param obj: The Section to be copied
        :type obj: Section
        :param children: Specify if the copy should be recursive
        :type children: bool
        :param keep_id: Specify if the id should be kept
        :type keep_id: bool
        :param name: Name of copied section, Default is name of source section
        :type name: str

        :returns: The copied section
        :rtype: Section
        """
        if not isinstance(obj, Section):
            raise TypeError("Object to be copied is not a Section")

        if obj._sec_parent:
            src = "{}/{}".format("sections", obj.name)
        else:
            src = "{}/{}".format("metadata", obj.name)
        clsname = "metadata"
        if not name:
            name = str(obj.name)
        sec = self._h5group.open_group("sections", True)
        if name in sec:
            raise NameError("Name already exist. Possible solution is to "
                            "provide a new name when copying destination "
                            "is the same as the source parent")
        obj._parent._h5group.copy(source=src, dest=self._h5group,
                                  name=name, cls=clsname,
                                  shallow=not children, keep_id=keep_id)

        if not children:
            for p in obj.props:
                self.sections[obj.name].create_property(copy_from=p,
                                                        keep_copy_id=keep_id)

        return self.sections[obj.name]

    def flush(self) -> None:
        self._h5file.flush()

    def close(self) -> None:
        """
        Closes an open file.
        """
        gc.collect()  # should handle refs better instead of calling collect()
        # Flush is probably unnecessary
        self._h5file.flush()
        self._h5file.close()

    # Block
    def create_block(self, name="", type_="", compression=Compression.Auto,
                     copy_from=None, keep_copy_id=True) -> Block:
        """
        Create a new block inside the file.

        :param name: The name of the block to create.
        :type name: str
        :param type_: The type of the block.
        :type type_: str
        :param compression: No, DeflateNormal, Auto (default: Auto)
        :param copy_from: The Block to be copied, None in normal mode
        :type copy_from: Block
        :param keep_copy_id: Specify if the id should be copied in copy mode
        :type keep_copy_id: bool

        :returns: The newly created block.
        :rtype: Block
        """
        if copy_from:
            if not isinstance(copy_from, Block):
                raise TypeError("Object to be copied is not a Block")
            clsname = "data"
            src = "{}/{}".format(clsname, copy_from.name)
            if not name:
                name = str(copy_from.name)
            if name in self._data:
                raise NameError("Name already exist. Possible solution is to "
                                "provide a new name when copying destination "
                                "is the same as the source parent")
            b = copy_from._parent._h5group.copy(source=src, dest=self._h5group,
                                                name=name,
                                                cls=clsname,
                                                keep_id=keep_copy_id)
            id_ = b.attrs["entity_id"]
            return self.blocks[id_]

        if name in self._data:
            raise ValueError("Block with the given name already exists!")
        if compression == Compression.Auto:
            compression = self._compr
        block = Block._create_new(self, self._data, name, type_, compression)
        return block

    # Section
    def create_section(self, name, type_="undefined", oid=None) -> Section:
        """
        Create a new metadata section inside the file.

        :param name: The name of the section to create.
        :type name: str
        :param type_: The type of the section.
        :type type_: str
        :param oid: object id, UUID string as specified in RFC 4122. If no id
                    is provided, an id will be generated and assigned.
        :type oid: str

        :returns: The newly created section.
        :rtype: Section
        """
        if name in self.metadata:
            raise DuplicateName("create_section")
        sec = Section._create_new(self, self.metadata, name, type_, oid)
        return sec

    @property
    def blocks(self) -> Container:
        """
        A property containing all blocks of a file. Blocks can be obtained by
        their name, id or index. Blocks can be deleted from the list, when a
        block is deleted all its content (data arrays, tags and sources) will
        be also deleted from the file. Adding new Block is done via the
        create_block method of File. This is a read-only attribute.
        """
        if self._blocks is None:
            self._blocks = Container("data", self, Block)
        return self._blocks

    def find_sections(self, filtr=lambda _: True, limit=None) -> List[Section]:
        """
        Get all sections and their child sections recursively.

        This method traverses the trees of all sections. The traversal is
        accomplished via breadth first and can be limited in depth. On each
        node or section a filter is applied. If the filter returns true the
        respective section will be added to the result list.
        By default a filter is used that accepts all sections.

        :param filtr: A filter function
        :type filtr:  function
        :param limit: The maximum depth of traversal
        :type limit:  int

        :returns: A list containing the matching sections.
        :rtype: list of Section
        """
        if limit is None:
            limit = maxint
        return finders._find_sections(self, filtr, limit)

    @property
    def sections(self) -> SectionContainer:
        """
        A property containing all root Sections of a file. Specific root
        Sections can be obtained by their name, id or index. Sections can be
        deleted from this list. Notice: when a section is deleted all its child
        section and properties will be removed too. Adding a new Section is
        done via the crate_section method of File.
        This is a read-only property.
        """
        if self._sections is None:
            self._sections = SectionContainer("metadata", self, Section)
        return self._sections


# Copy File constructor docstring to File.open
File.open.__func__.__doc__ = File.__init__.__doc__
