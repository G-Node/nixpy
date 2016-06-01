# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from uuid import uuid4, UUID


def sanitizer(name):
    return name.replace("/", "_")


def check(name):
    return "/" not in name


def create_id():
    return str(uuid4())
