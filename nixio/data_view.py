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
        self._count = tuple(count)
        self._offset = tuple(offset)

        co = tuple(c + o for c, o in zip(self._count, self._offset))
        if any(c > e for c, e in zip(co, self.array.data_extent)):
            raise OutOfBounds(
                "Trying to create DataView which is out of bounds"
            )

    @property
    def data_extent(self):
        return self._count

    @property
    def data_type(self):
        return self.array.data_type

    def _write_data(self, data, count, offset):
        if not count:
            count = self._count
        offset = self._transform_coordinates(count, offset)
        return super(DataView, self)._write_data(data, count, offset)

    def _read_data(self, data, count, offset):
        if not count:
            count = self._count
        offset = self._transform_coordinates(count, offset)
        return super(DataView, self)._read_data(data, count, offset)

    def _transform_coordinates(self, count, offset):
        if not offset:
            if np.any(np.greater(count, self._count)):
                raise OutOfBounds("Trying to access data outside of range")
            return self._offset
        else:
            co = tuple(c + o for c, o in zip(count, offset))
            if any(c > sc for c, sc in zip(co, self._count)):
                raise OutOfBounds("Trying to access data outside of range")
            return tuple(so + o for so, o in zip(self._offset, offset))
