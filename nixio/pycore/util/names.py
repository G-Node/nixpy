# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def sanitizer(name):
    """
    Sanitizes a string supposed to be an entity name. That is,
    invalid characters like slashes are substituted with underscores.

    :param name: A string representing the name.

    :returns: The sanitized name.
    :rtype: str
    """
    return name.replace("/", "_")


def check(name):
    """
    Checks a string whether is needs to be sanitized.

    :param name: The name.

    :returns: True if the name is valid, false otherwise.
    :rtype: bool
    """
    if isinstance(name, bytes):
        name = name.decode()
    return "/" not in name
