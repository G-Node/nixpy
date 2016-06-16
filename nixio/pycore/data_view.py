# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import numpy as np

from .data_array import DataSet
from .exceptions import OutOfBounds


class DataView(DataSet):

    def __init__(self, da, count, offset):
        self.array = da
        self._h5group = self.array._h5group
        self.count = count
        self.offset = offset

        if np.all(np.greater(np.add(self.count, self.offset),
                             self.array.data_extent)):
            raise OutOfBounds(
                "Trying to create DataView which is out of bounds"
            )

    @property
    def data_extent(self):
        return self.count

