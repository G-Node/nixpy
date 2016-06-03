# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from . import util


class H5Group(object):

    def __init__(self, parent, name, create=False):
        self.parent = parent
        self.name = name
        self.h5obj = None
        if create or name in self.parent:
            self._create_h5obj()

    def _create_h5obj(self):
        self.h5obj = self.parent.require_group(self.name)

    def create_group(self, name, create=False):
        self._create_h5obj()
        return H5Group(self.h5obj, name, create)

    def get_by_id(self, id_or_name):
        if not self.h5obj:
            raise ValueError
        if util.is_uuid(id_or_name):
            for item in self.h5obj.values():
                if item.attrs["id"] == id_or_name:
                    break
            else:
                raise ValueError
        else:
            try:
                item = self.h5obj[id_or_name]
            except Exception:
                raise ValueError
        return item

    def pos_getter(self, pos):
        if not self.h5obj:
            raise ValueError
        return list(self.h5obj.values())[pos]

    def deleter(self, id_or_name):
        if util.is_uuid(id_or_name):
            name = self.get_by_id(id_or_name).name
        else:
            name = id_or_name
        try:
            del self.h5obj[name]
        except Exception:
            raise ValueError
        # Delete if empty
        if not len(self.h5obj):
            del self.h5obj
            self.h5obj = None

    def set_attr(self, name, value):
        self._create_h5obj()
        self.h5obj.attrs[name] = value

    def get_attr(self, name):
        return self.h5obj.attrs[name]

    def __contains__(self, item):
        return item in self.h5obj
