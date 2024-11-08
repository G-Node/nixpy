# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import numpy as np

import h5py
from datetime import datetime, timezone
from uuid import uuid4, UUID
from ..exceptions import exceptions
from . import names


vlen_str_dtype = h5py.string_dtype(encoding='utf-8', length=None)


def create_id():
    """
    Creates an ID as used for nix entities.

    :returns: The ID.
    :rtype: str
    """
    return str(uuid4())


def is_uuid(id_str):
    try:
        UUID(str(id_str))
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


def time_to_str(time):
    """
    Returns the time represented by the parameter in the format of Boost's
    posix time `to_iso_string` function.

    :param time: integer POSIX time
    :type time: int

    :return: string in the form "YYYYMMDDTHHMMSS", where T is the date-time separator
    :rtype: str
    """
    dt = datetime.fromtimestamp(time, timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%S").encode("utf-8")


def str_to_time(time_str):
    """
    Returns the POSIX time represented by the given string as an integer.

    :param time_str: string in the form "YYYYMMDDTHHMMSS", where T is the date-time separator
    :type time_str: str

    :return: integer POSIX time
    :rtype: int
    """
    if isinstance(time_str, bytes):
        time_str = time_str.decode()
    dt = datetime.strptime(time_str, "%Y%m%dT%H%M%S") - datetime(1970, 1, 1)
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
    if value is not None and not isinstance(value, type_):
        raise exceptions.InvalidAttrType(type_, value)


def apply_polynomial(coefficients, origin, data):
    data[:] = data[:] - origin
    if coefficients:
        data[:] = np.polynomial.polynomial.polyval(data, coefficients)
