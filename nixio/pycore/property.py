# Copyright (c) 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import numpy as np
from .entity import Entity
from ..property import PropertyMixin


class Property(Entity, PropertyMixin):

    def __init__(self, h5obj):
        super(Property, self).__init__(h5obj)

    def delete_values(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass
