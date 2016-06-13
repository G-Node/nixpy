# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import absolute_import
import os

import h5py
import numpy as np

from .h5group import H5Group

from .util import util
from . import Block
from . import exceptions
from . import Section

from ..file import FileMixin

try:
    from nixio.core import File as CFile
except ImportError:
    CFile = None


class FileMode(object):
    ReadOnly = 'r'
    ReadWrite = 'a'
    Overwrite = 'w'


class File(FileMixin):

    def __init__(self, path, mode=FileMode.ReadWrite):
        if not os.path.exists(path):
            mode = FileMode.Overwrite
        if os.path.isfile(path):
            self._open_existing(path, mode)
        else:
            self._create_new(path, mode)

        self._root = H5Group(self._h5file, "/", create=True)
        self._data = self._root.open_group("data", create=True)
        self.metadata = self._root.open_group("metadata", create=True)
        if "created_at" not in self._h5file.attrs:
            self.force_created_at()
        if "updated_at" not in self._h5file.attrs:
            self.force_updated_at()

    def _open_existing(self, path, mode):
        self._h5file = h5py.File(name=path, mode=mode)
        if mode == FileMode.Overwrite:
            self._create_header()

    def _create_new(self, path, mode):
        self._h5file = h5py.File(name=path, mode=mode)
        self._create_header()

    def _create_header(self):
        self.format = "nix"
        self.version = (1, 0, 0)

    @classmethod
    def open(cls, path, mode, backend="hdf5"):
        if backend == "hdf5":
            if CFile:
                return CFile.open(path, mode)
            else:
                # TODO: Brief instructions or web URL for building C++ files?
                raise RuntimeError("HDF5 backend is not available.")
        elif backend == "h5py":
            return cls(path, mode)
        else:
            raise ValueError("Valid backends are 'hdf5' and 'h5py'.")

    @property
    def version(self):
        return tuple(self._h5file.attrs["version"])

    @version.setter
    def version(self, v):
        util.check_attr_type(v, tuple)
        for part in v:
            util.check_attr_type(part, int)
        self._h5file.attrs["version"] = v

    @property
    def format(self):
        return self._h5file.attrs["format"].decode()

    @format.setter
    def format(self, f):
        util.check_attr_type(f, str)
        self._h5file.attrs["format"] = f.encode("utf-8")

    @property
    def created_at(self):
        return util.str_to_time(self._h5file.attrs["created_at"])

    def force_created_at(self, t=util.now_int()):
        util.check_attr_type(t, int)
        self._h5file.attrs["created_at"] = util.time_to_str(t)

    @property
    def updated_at(self):
        return util.str_to_time(self._h5file.attrs["updated_at"])

    def force_updated_at(self, t=util.now_int()):
        util.check_attr_type(t, int)
        self._h5file.attrs["updated_at"] = util.time_to_str(t)

    def is_open(self):
        pass

    def close(self):
        self._h5file.close()

    def validate(self):
        pass

    # Block
    def create_block(self, name, type_):
        if name in self._data:
            raise ValueError("Block with the given name already exists!")
        block = Block._create_new(self._data, name, type_)
        return block

    def _get_block_by_id(self, id_or_name):
        return Block(self._data.get_by_id_or_name(id_or_name))

    def _get_block_by_pos(self, pos):
        return Block(self._data.get_by_pos(pos))

    def _delete_block_by_id(self, id_or_name):
        self._data.delete(id_or_name)

    def _block_count(self):
        return len(self._data)

    # Section
    def create_section(self, name, type_):
        if name in self.metadata:
            raise exceptions.DuplicateName("create_section")
        sec = Section._create_new(self.metadata, name, type_)
        return sec

    def _get_section_by_id(self, id_or_name):
        return Section(self.metadata.get_by_id_or_name(id_or_name))

    def _get_section_by_pos(self, pos):
        return Section(self.metadata.get_by_pos(pos))

    def _delete_section_by_id(self, id_or_name):
        self.metadata.delete(id_or_name)

    def _section_count(self):
        return len(self.metadata)


