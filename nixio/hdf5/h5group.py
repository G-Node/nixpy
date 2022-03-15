# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import h5py
import numpy as np

from .h5dataset import H5DataSet
from ..datatype import DataType

from .. import util


class H5Group(object):

    def __init__(self, parent, name, create=False):
        self._parent = parent
        self.name = name
        self.group = None
        if create or name in self._parent:
            self._create_h5obj()
        self.h5obj = self.group

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

    @property
    def group(self):
        if self._group is None:
            if self.name in self._parent:
                self._group = self._parent[self.name]
            else:
                return None
        return self._group

    @group.setter
    def group(self, grp):
        self._group = grp

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

    def create_dataset(self, name, shape, dtype, compression=False):
        """
        Creates a dataset object under the current group with a given name,
        shape, and type.

        :param name: the name of the dataset
        :param shape: tuple representing the shape of the dataset
        :param dtype: the type of the data for this dataset (DataType)
        :param compression: whether to compress the data (default: False)
        :return: a new H5DataSet object
        """
        self._create_h5obj()
        return H5DataSet(self.group, name, dtype, shape, compression)

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

    def write_data(self, name, data, dtype=None, compression=False):
        """
        Writes the data to a Dataset contained in the group with the
        given name. Creates the Dataset if necessary.

        :param name: name of the Dataset object
        :param data: the data to write
        :param dtype: optionally specify the data type, otherwise it will be
        automatically determined by the data
        :param compression: whether to compress the data (default: False)
        """
        shape = np.shape(data)
        if self.has_data(name):
            dset = self.get_dataset(name)
            dset.shape = shape
        else:
            if dtype is None:
                dtype = DataType.get_dtype(data[0])
            dset = self.create_dataset(name, shape, dtype, compression)

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
            raise KeyError("Item not found '{}'".format(name))

    def get_by_id(self, id_):
        if self.group:
            for item in self:
                if item.get_attr("entity_id") == id_:
                    return item
        raise KeyError("Item not found '{}'".format(id_))

    def get_by_pos(self, pos):
        if not self.group:
            raise IndexError

        # Using low level interface to specify iteration order
        name, _ = self.group.id.links.iterate(lambda n: n,
                                              idx_type=h5py.h5.INDEX_CRT_ORDER,
                                              order=h5py.h5.ITER_INC,
                                              idx=pos)
        return self.get_by_name(name)

    def delete(self, id_or_name, delete_if_empty=True):
        """
        Deletes the child HDF5 group that matches the given name or id.
        """
        if util.is_uuid(id_or_name):
            name = self.get_by_id_or_name(id_or_name).name
        else:
            name = id_or_name
        try:
            del self.group[name]
        except Exception:
            raise ValueError("Error deleting {} ".format(name))
        # Delete if empty and non-root container
        groupdepth = len(self.group.name.split("/")) - 1
        if delete_if_empty and not len(self.group) and groupdepth > 1:
            del self.parent.group[self.name]
            # del self.group
            self.group = None

    def delete_all(self, eid):
        """
        Deletes all references to a given list of objects, identified by their
        entity_id, below the current object.
        """
        # Use visit_items to traverse groups and check their children.
        # visit_items visits each item only once, so instead of checking
        # whether each item is the one we're searching for, we check whether
        # it *contains* the one we're searching for
        # We delete the child as soon as we find it; this doesn't cause
        # iteration issues since it's deleted before descending into the
        # children of the current group

        def delete_by_id(_, obj):
            if not isinstance(obj, h5py.Group):
                return
            grp = self.create_from_h5obj(obj)
            for child in grp:
                if child.get_attr("entity_id") in eid:
                    del grp[child.name]

        self._group.visititems(delete_by_id)

    def set_attr(self, name, value):
        self._create_h5obj()
        if value is None:
            if name in self.group.attrs:
                del self.group.attrs[name]
        else:
            if isinstance(value, np.str_):
                value = str(value)
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

        def match(name, obj):
            curdepth = len(name.split("/"))
            if limit is not None and curdepth > limit:
                return None

            h5grp = H5Group.create_from_h5obj(obj)
            if filtr is None or filtr(h5grp):
                result.append(h5grp)

        self.group.visititems(match)
        return result

    def copy(self, source, dest, name=None, cls=None, shallow=False,
             keep_id=True):
        grp = self.group
        dest.open_group(cls, create=True)
        dest_grp = dest.group[cls]
        grp.copy(source=source, dest=dest_grp, name=name, shallow=shallow)

        grp = dest_grp[name]
        grp.attrs["name"] = name
        if not keep_id:
            def change_id(_, igrp):
                if "entity_id" in igrp.attrs:
                    id_ = util.create_id()
                    igrp.attrs.modify("entity_id", np.string_(id_))
            id_ = util.create_id()
            grp.attrs.modify("entity_id", np.string_(id_))
            grp.visititems(change_id)
        return grp

    @property
    def parent(self):
        return self.create_from_h5obj(self._parent)

    def __iter__(self):
        if not len(self):
            return
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
