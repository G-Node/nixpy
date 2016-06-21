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
from datetime import datetime
from uuid import uuid4, UUID
from ..exceptions import exceptions
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
    if entity is not None:
        return True
    if raise_exception:
        raise exceptions.UninitializedEntity()
    return False


def now_int():
    return int(time())


def time_to_str(t):
    """
    Returns the time represented by the parameter in the format of Boost's
    posix time `to_iso_string` function.

    :param t: integer POSIX time
    :return: string in the form "YYYYMMDDTHHMMSS", where T is the date-time
    separator
    """
    dt = datetime.fromtimestamp(t)
    return dt.strftime("%Y%m%dT%H%M%S").encode("utf-8")


def str_to_time(s):
    """
    Returns the POSIX time represented by the given string as an integer.

    :param s: string in the form "YYYYMMDDTHHMMSS", where T is the date-time
    separator
    :return: integer POSIX time
    """
    dt = datetime.strptime(s.decode(), "%Y%m%dT%H%M%S")
    return int(dt.strftime("%s"))


def check_attr_type(value, type_):
    """
    Checks if a value is of a given type and raises an exception if the check
     fails. The check does not fail if value is None.

    :param value: the value to check
    :param type_: the type to check against
    """
    if value is not None and not isinstance(value, type_):
        raise exceptions.InvalidAttrType(type_, value)


def co_to_slice(count, offset):
    """
    Converts an offset-count pair to an h5py compatible slice

    :param count: number of items
    :param offset: offset from start
    :return: slice-like tuple or single index
    """
    sl = []
    for c, o in zip(count, offset):
        sl.append(slice(o, c+o))
    if len(sl) == 1:
        return sl[0]
    else:
        return tuple(sl)
