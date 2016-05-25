# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from .entity import Entity


class LinkType(object):
    Tagged = 1
    Untagged = 2
    Indexed = 3


class Feature(Entity):

    def __init__(self):
        super(Feature, self).__init__()
        self.link_type = None
        self.data = None
