# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from . import util
from .h5dataset import H5DataSet


class H5Group(object):

    def __init__(self, parent, name, create=False):
        self._parent = parent
        self.name = name
        self.group = None
        if create or name in self._parent:
            self._create_h5obj()

    def _create_h5obj(self):
        self.group = self._parent.require_group(self.name)

    @classmethod
    def create_from_h5obj(cls, h5obj):
        parent = h5obj.parent
        name = h5obj.name.split("/")[-1]
        return cls(parent, name)

    def open_group(self, name, create=False):
        """
        Returns a new H5Group with the given name contained in the current group.
        If the current group does not exist in the file, it is automatically
        created.

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
        Returns a contained dataset (H5DataSet) object.

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

    def get_data(self, name):
        """
        Returns the data contained in the dataset identified by 'name', or None
        if the a dataset of that name does not exist in the Group.

        :param name: The name of the dataset
        :return: The data contained in the dataset as a numpy array or None
        """
        if name not in self.group:
            return tuple()

        dset = self.group[name]
        # TODO: Error if dset is Group?
        return dset[:]

    def add_by_id(self, id_or_name):
        self._create_h5obj()
        parblock = self.parent.parent.parent
        parcontainer = parblock.open_group(self.name)
        target = parcontainer.get_by_id_or_name(id_or_name)
        self.group[target.get_attr("name")] = target.group

    def has_by_id(self, id_or_name):
        if not self.group:
            return False
        if util.is_uuid(id_or_name):
            for item in self.group:
                if item.attrs["id"] == id_or_name:
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
            for item in self.group.values():
                if item.attrs["id"] == id_:
                    return self.create_from_h5obj(item)
        raise ValueError("No item with ID {} found in {}".format(
            id_, self.group.name
        ))

    def get_by_pos(self, pos):
        if not self.group:
            raise ValueError
        return self.create_from_h5obj(list(self.group.values())[pos])

    def delete(self, id_or_name):
        if util.is_uuid(id_or_name):
            name = self.get_by_id_or_name(id_or_name).name
        else:
            name = id_or_name
        try:
            del self.group[name]
        except Exception:
            raise ValueError
        # Delete if empty and non-root container
        groupdepth = len(self.group.name.split("/")) - 1
        if not len(self.group) and groupdepth > 1:
            del self.group
            self.group = None

    def set_attr(self, name, value):
        self._create_h5obj()
        if value is None:
            del self.group.attrs[name]
        else:
            self.group.attrs[name] = value

    def get_attr(self, name):
        return self.group.attrs.get(name)

    @property
    def parent(self):
        return self.create_from_h5obj(self._parent)

    def __contains__(self, item):
        if self.group is None:
            return False
        return item in self.group

    def __len__(self):
        if self.group is None:
            return 0
        else:
            return len(self.group)

    def __str__(self):
        return "<H5Group object: {}>".format(self.group.name)

