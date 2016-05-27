# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
# -*- coding: utf-8 -*-
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import h5py
from time import time
from uuid import uuid4, UUID
from .. import exceptions
from . import names

try:
    unicode = unicode
except NameError:
    unicode = str


vlen_str_dtype = h5py.special_dtype(vlen=unicode)


def is_uuid(id_):
    try:
        UUID(str(id_))
        return True
    except ValueError:
        return False


def check_entity_name_and_type(name, type_):
    check_entity_name(name)
    check_entity_type(type_)


def check_entity_type(type_):
    if not type_:
        raise ValueError("String provided for entity type is empty!")


def check_entity_name(name):
    if not name:
        raise ValueError("String provided for entity name is empty!")
    if not names.check(name):
        raise ValueError("String provided for entity name is invalid!")


def check_entity_id(id_):
    if not is_uuid(id_):
        raise ValueError("String provided for id is not a valid UUID")


def check_empty_str(string, field_name):
    if not string:
        raise ValueError("String provided is empty! {}".format(field_name))


def check_name_or_id(name_or_id):
    if not name_or_id:
        raise ValueError("String provided for entity name is empty!")


def check_entity_input(entity, raise_exception=True):
    if entity:
        return True
    if raise_exception:
        raise exceptions.UninitializedEntity()
    return False


def now():
    return int(time())


def create_h5props(cls, attributes, types=None):

    def makeprop(propname, type_):

        def getter(self):
            value = self._h5obj.attrs.get(propname)
            if type_ is not None and value is not None:
                value = type_(value)
            return value

        def setter(self, value):
            if value is None:
                if propname == "type":
                    raise AttributeError("type can't be None")
                del self._h5obj.attrs[propname]
                return
            if type_ and not isinstance(value, type_):
                raise TypeError("Attribute {} requires type {} but {} "
                                "was provided".format(propname, type_,
                                                      type(value)))
            if propname in ("name", "id") and propname in self._h5obj.attrs:
                raise AttributeError("can't set attribute")
            self._h5obj.attrs[propname] = value

        def deleter(self):
            # TODO: Allow deleting attributes?
            # TODO: Do not allow deleting required attributes (name, type, id)
            del self._h5obj.attrs[propname]

        return property(fget=getter, fset=setter, fdel=deleter)

    if types is None:
        types = [None]*len(attributes)
    for attr, type_ in zip(attributes, types):
        setattr(cls, attr, makeprop(attr, type_))


def create_container_methods(cls, chcls, chclsname, container=None):
    # TODO: Better exception handling and messages

    if container is None:
        container = chclsname + "s"

    def id_or_name_getter(self, id_or_name):
        if is_uuid(id_or_name):
            for h5obj in self._h5obj[container].values():
                if h5obj.attrs["id"] == id_or_name:
                    break
            else:
                raise ValueError
        else:
            try:
                h5obj = self._h5obj[container][id_or_name]
            except Exception:
                raise ValueError
        return chcls(h5obj)

    def pos_getter(self, pos):
        obj = list(self._h5obj[container].values())[pos]
        return chcls(obj)

    def deleter(self, id_or_name):
        if is_uuid(id_or_name):
            name = id_or_name_getter(self, id_or_name).name
        else:
            name = id_or_name
        try:
            del self._h5obj[container][name]
        except Exception:
            raise ValueError

    def counter(self):
        return len(self._h5obj[container])

    setattr(cls, "_get_{}_by_id".format(chclsname), id_or_name_getter)
    setattr(cls, "_get_{}_by_pos".format(chclsname), pos_getter)
    setattr(cls, "_delete_{}_by_id".format(chclsname), deleter)
    setattr(cls, "_{}_count".format(chclsname), counter)


def create_link_methods(cls, chcls, chclsname, container=None):

    if container is None:
        container = chclsname + "s"

    def adder(self, id_or_name):
        parent = self._h5obj.parent.parent
        if is_uuid(id_or_name):
            for h5obj in parent[container].values():
                if h5obj.attrs["id"] == id_or_name:
                    break
            else:
                raise KeyError("Group add {type}: "
                               "{type} not found in parent Block!"
                               .format(type=chcls.__name__))
        else:
            try:
                h5obj = parent._h5obj[container][id_or_name]
            except KeyError:
                raise KeyError("Group add {type}: "
                               "{type} not found in parent Block!"
                               .format(type=chcls.__name__))

        self._h5obj[container][h5obj.attrs["name"]] = h5obj

    def containschecker(self, id_or_name):
        if is_uuid(id_or_name):
            for h5obj in self._h5obj[container]:
                if h5obj.attrs["id"] == id_or_name:
                    return True
            else:
                return False
        else:
            return id_or_name in self._h5obj[container]

    setattr(cls, "_add_{}_by_id".format(chclsname), adder)
    setattr(cls, "_has_{}_by_id".format(chclsname), containschecker)

