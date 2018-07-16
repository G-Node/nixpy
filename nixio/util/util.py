# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from six import string_types
import numpy as np

import h5py
from datetime import datetime
from uuid import uuid4, UUID
from ..exceptions import exceptions
from . import names

from nixio.link_type import LinkType


try:
    vstype = unicode
except NameError:
    vstype = str


vlen_str_dtype = h5py.special_dtype(vlen=vstype)


def create_id():
    """
    Creates an ID as used for nix entities.

    :returns: The ID.
    :rtype: str
    """
    return str(uuid4())


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
    """
    Returns the current POSIX time as an integer.

    :return: integer POSIX time
    """
    now = datetime.now() - datetime(1970, 1, 1)
    return int(now.total_seconds())


def time_to_str(t):
    """
    Returns the time represented by the parameter in the format of Boost's
    posix time `to_iso_string` function.

    :param t: integer POSIX time
    :return: string in the form "YYYYMMDDTHHMMSS", where T is the date-time
    separator
    """
    dt = datetime.utcfromtimestamp(t)
    return dt.strftime("%Y%m%dT%H%M%S").encode("utf-8")


def str_to_time(s):
    """
    Returns the POSIX time represented by the given string as an integer.

    :param s: string in the form "YYYYMMDDTHHMMSS", where T is the date-time
    separator
    :return: integer POSIX time
    """
    if isinstance(s, bytes):
        s = s.decode()
    dt = datetime.strptime(s, "%Y%m%dT%H%M%S") - datetime(1970, 1, 1)
    return int(dt.total_seconds())


def check_attr_type(value, type_):
    """
    Checks if a value is of a given type and raises an exception if the check
    fails. The check does not fail if value is None.
    Specifying `str` for type checks against all string types
    (str, bytes, basestring).


    :param value: the value to check
    :param type_: the type to check against
    """
    if type_ is str:
        type_ = string_types
    if value is not None and not isinstance(value, type_):
        raise exceptions.InvalidAttrType(type_, value)


def apply_polynomial(coefficients, origin, data):
    data[:] = data[:] - origin
    if coefficients:
        data[:] = np.polynomial.polynomial.polyval(data, coefficients)


# The following two functions currently behave as capitalised <-> lowercase
# converters, but they are general solutions for alternate implementations of
# LinkType (e.g., enum)
def link_type_to_string(lt):
    if lt == LinkType.Indexed:
        return "indexed"
    elif lt == LinkType.Tagged:
        return "tagged"
    elif lt == LinkType.Untagged:
        return "untagged"
    else:
        raise RuntimeError("Invalid LinkType")


def link_type_from_string(ltstr):
    if ltstr == "indexed":
        return LinkType.Indexed
    elif ltstr == "tagged":
        return LinkType.Tagged
    elif ltstr == "untagged":
        return LinkType.Untagged
    else:
        raise RuntimeError("Invalid string for LinkType")
