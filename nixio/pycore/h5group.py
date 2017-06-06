# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)

import h5py
import numpy as np

from .h5dataset import H5DataSet
from ..value import DataType
from .block import Block
from .section import Section

from . import util
from .exceptions import InvalidEntity


class H5Group(object):

    def __init__(self, parent, name, create=False):
        self._parent = parent
        self.name = name
        self.group = None
        if create or name in self._parent:
            self._create_h5obj()

    def _create_h5obj(self):
        if self.name in self._parent:
            self.group = self._parent[self.name]
        else:
            gcpl = h5py.h5p.create(h5py.h5p.GROUP_CREATE)
            flags = h5py.h5p.CRT_ORDER_TRACKED | h5py.h5p.CRT_ORDER_INDEXED
            gcpl.set_link_creation_order(flags)
            name = self.name.encode("utf-8")
            gid = h5py.h5g.create(self._parent.id, name, gcpl=gcpl)
            self.group = h5py.Group(gid)

    def create_link(self, target, name):
        self._create_h5obj()
        if name in self.group:
            del self.group[name]
        self.group[name] = target._h5group.group

    @classmethod
    def create_from_h5obj(cls, h5obj):
        parent = h5obj.parent
        name = h5obj.name.split("/")[-1]
        if isinstance(h5obj, h5py.Group):
            return cls(parent, name)
        elif isinstance(h5obj, h5py.Dataset):
            return H5DataSet(parent, name)
        else:
            raise ValueError("Invalid object: "
                             "{} must be either h5py.Group of h5py.Dataset.")

    def open_group(self, name, create=False):
        """
        Returns a new H5Group with the given name contained in the current
        group.  If the current group does not exist in the file,
        it is automatically created.

        :param name: the name of the group
        :param create: creates the child group in the file if it does not exist
        :return: a new H5Group object
        """
        self._create_h5obj()
        return H5Group(self.group, name, create)

    def create_dataset(self, name, shape, dtype):
        """
        Creates a dataset object under the current group with a given name,
        shape, and type.

        :param name: the name of the dataset
        :param shape: tuple representing the shape of the dataset
        :param dtype: the type of the data for this dataset (DataType)
        :return: a new H5DataSet object
        """
        self._create_h5obj()
        return H5DataSet(self.group, name, dtype, shape)

    def get_dataset(self, name):
        """
        Returns a contained H5DataSet object.

        :param name: name of the dataset
        :return: H5DataSet object
        """
        notfound = KeyError("No DataSet named {} found.")
        if self.group is None:
            raise notfound
        if name in self.group:
            dset = self.group[name]
            return H5DataSet.create_from_h5obj(dset)
        else:
            raise notfound

    def write_data(self, name, data, dtype=None):
        """
        Writes the data to a Dataset contained in the group with the
        given name.  Creates the Dataset if necessary.

        :param name: name of the Dataset object
        :param data: the data to write
        :param dtype: optionally specify the data type, otherwise it will be
        automatically determined by the data
        """
        shape = np.shape(data)
        if self.has_data(name):
            dset = self.get_dataset(name)
            dset.shape = shape
        else:
            if dtype is None:
                dtype = DataType.get_dtype(data[0])
            dset = self.create_dataset(name, shape, dtype)

        dset.write_data(data)

    def get_data(self, name):
        """
        Returns the data contained in the dataset identified by 'name', or an
        empty list if a dataset of that name does not exist in the Group.

        :param name: The name of the dataset
        :return: The data contained in the dataset as a numpy array or None
        """
        if name not in self.group:
            return []

        dset = self.group[name]
        # TODO: Error if dset is Group?
        return dset[:]

    def has_data(self, name):
        """
        Return True if the Group contains a Dataset object with the given name.

        :param name: name of Dataset
        :return: True if Dataset exists in Group, False if it does not exist,
        or exists and is not a Dataset
        """
        if self.group.get(name, getclass=True) == h5py.Dataset:
            return True
        else:
            return False

    def has_by_id(self, id_or_name):
        if not self.group:
            return False
        if util.is_uuid(id_or_name):
            for item in self:
                if item.get_attr("entity_id") == id_or_name:
                    return True
            else:
                return False
        else:
            return id_or_name in self.group

    def get_by_id_or_name(self, id_or_name):
        if util.is_uuid(id_or_name):
            return self.get_by_id(id_or_name)
        else:
            return self.get_by_name(id_or_name)

    def get_by_name(self, name):
        if self.group and name in self.group:
            return self.create_from_h5obj(self.group[name])
        else:
            raise ValueError("No item with name {} found in {}".format(
                name, self.group.name
            ))

    def get_by_id(self, id_):
        if self.group:
            for item in self:
                if item.get_attr("entity_id") == id_:
                    return item
        raise ValueError("No item with ID {} found in {}".format(
            id_, self.name
        ))

    def get_by_pos(self, pos):
        if not self.group:
            raise ValueError

        # Using low level interface to specify iteration order
        name, _ = self.group.id.links.iterate(lambda n: n,
                                              idx_type=h5py.h5.INDEX_CRT_ORDER,
                                              order=h5py.h5.ITER_INC,
                                              idx=pos)
        return self.get_by_name(name)

    def delete(self, id_or_name):
        if util.is_uuid(id_or_name):
            name = self.get_by_id_or_name(id_or_name).name
        else:
            name = id_or_name
        try:
            del self.group[name]
        except Exception:
            raise ValueError("Error deleting {} from {}".format(name,
                                                                self.name))
        # Delete if empty and non-root container
        groupdepth = len(self.group.name.split("/")) - 1
        if not len(self.group) and groupdepth > 1:
            del self.parent.group[self.name]
            # del self.group
            self.group = None

    def set_attr(self, name, value):
        self._create_h5obj()
        if value is None:
            if name in self.group.attrs:
                del self.group.attrs[name]
        else:
            self.group.attrs[name] = value

    def get_attr(self, name):
        if self.group is None:
            return None
        attr = self.group.attrs.get(name)
        if isinstance(attr, bytes):
            attr = attr.decode()
        return attr

    def find_children(self, filtr=None, limit=None):

        result = []
        start_depth = len(self.group.name.split("/"))

        def match(name, obj):
            curdepth = name.split("/")
            if limit is not None and curdepth == start_depth + limit:
                return None

            h5grp = H5Group.create_from_h5obj(obj)
            if filtr(h5grp):
                result.append(h5grp)

        self.group.visititems(match)
        return result

    @property
    def file(self):
        """
        An H5Group object which represents the file root.

        :return: H5Group at '/'
        """
        return H5Group(self.group.file, "/", create=False)

    @property
    def h5root(self):
        """
        Returns the H5Group of the Block or top-level Section which contains
        this object. Returns None if requested on the file root '/' or the
        /data or /metadata groups.

        :return: Top level object containing this group (H5Group)
        """
        pathparts = self.group.name.split("/")
        if len(pathparts) == 3:
            return self
        if self.group.name == "/":
            return None
        if len(pathparts) == 2:
            return None

        return self.parent.h5root

    @property
    def root(self):
        """
        Returns the Block or top-level Section which contains this object.
        Returns None if requested on the file root '/' or the /data or
        /metadata groups.

        :return: Top level object containing this group (Block or Section)
        """
        h5root = self.h5root
        if h5root is None:
            return None
        topgroup = self.group.name.split("/")[1]
        if topgroup == "data":
            cls = Block
        elif topgroup == "metadata":
            cls = Section
        else:
            raise InvalidEntity
        return cls(h5root)

    @property
    def parent(self):
        return self.create_from_h5obj(self._parent)

    def __iter__(self):
        for grp in self.group.values():
            yield self.create_from_h5obj(grp)

    def __contains__(self, item):
        if self.group is None:
            return False
        return item in self.group

    def __len__(self):
        if self.group is None:
            return 0
        else:
            return len(self.group)

    def __delitem__(self, key):
        del self.group[key]

    def __str__(self):
        return "<H5Group object: {}>".format(self.group.name)
