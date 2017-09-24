# Copyright (c) 2017, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from collections import namedtuple


IdentBase = namedtuple("IdentBase", ["name", "id"])


class Identity(IdentBase):

    def __new__(cls, name=None, id_=None):
        if not (name or id_):
            raise ValueError("Must specify at least one of name or id")

        if name is None:
            name = ""
        if id_ is None:
            id_ = ""
        new = super(Identity, cls).__new__(cls, name, id_)
        return new
