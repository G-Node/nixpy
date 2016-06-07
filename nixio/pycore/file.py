# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import absolute_import

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
        self._h5file = h5py.File(name=path, mode=mode)
        self.format = "nix"
        self.version = (1, 0, 0)
        self.created_at = util.now()
        self.updated_at = util.now()
        self._root = H5Group(self._h5file, "/", create=True)
        self._data = self._root.open_group("data", create=True)
        self.metadata = self._root.open_group("metadata", create=True)

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

    def force_created_at(self, t):
        self.created_at = t

    def force_updated_at(self, t):
        self.updated_at = t

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

    def is_open(self):
        pass

    def close(self):
        self._h5file.close()

    def validate(self):
        pass

