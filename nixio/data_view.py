# -*- coding: utf-8 -*-
# Copyright © 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import numpy as np
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
from .data_set import DataSet
from .exceptions import OutOfBounds, IncompatibleDimensions


class DataView(DataSet):

    def __init__(self, da, slices):
        if len(slices) != len(da.shape):
            # This is always checked by the calling function, but we repeat
            # the check here for future bug catching
            raise IncompatibleDimensions(
                "Number of dimensions for DataView does not match underlying "
                "DataArray: {} != {}".format(len(slices), len(da.shape)),
                "DataView"
            )

        if any(s.stop > e for s, e in zip(slices, da.data_extent)):
            raise OutOfBounds(
                "Trying to create DataView which is out of bounds of the "
                "underlying DataArray"
            )

        # Simplify all slices
        slices = tuple(slice(*sl.indices(dimlen))
                       for sl, dimlen in zip(slices, da.shape))

        self.array = da
        self._h5group = self.array._h5group
        self._slices = slices

    @property
    def data_extent(self):
        return tuple(s.stop - s.start for s in self._slices)

    @data_extent.setter
    def data_extent(self, v):
        raise AttributeError("can't set attribute")

    @property
    def data_type(self):
        return self.array.data_type

    def _write_data(self, data, sl=None):
        tsl = self._slices
        if sl:
            tsl = self._transform_coordinates(sl)
        super(DataView, self)._write_data(data, tsl)

    def _read_data(self, sl=None):
        # tsl = self._slices
        # if sl:
        #     tsl = self._transform_coordinates(sl)
        # return super(DataView, self)._read_data(tsl)
        dvslices = self._slices
        # complete DataView slices (turn Nones into values)
        dvslices = tuple(slice(*dv.indices(l)) for dv, l in
                         zip(dvslices, self.array.shape))
        sup = super(DataView, self)
        if sl is None or sl == slice(None, None, None):
            # full DataView: pass dvslices directly
            return sup._read_data(dvslices)
        if isinstance(sl, int):
            # single value or dimension, offset by DataView start on first dim
            readslice = dvslices[0].start + sl
            return sup._read_data(readslice)
        if isinstance(sl, Iterable):
            # combine slices
            readslice = list()
            for readi, datai in zip(sl, dvslices):
                if readi is None:
                    readslice.append(datai)
                elif isinstance(readi, int):
                    readslice.append(datai.start + readi)
                elif isinstance(readi, slice):
                    start = datai.start + (readi.start or 0)
                    stop = (datai.start + readi.stop
                            if readi.stop else datai.stop)
                    readslice.append(slice(start, stop, readi.step))
            return sup._read_data(tuple(readslice))

        # something else? Just read the underlying data then slice it
        # probably inefficient, but correct
        return sup._read_data(dvslices).read_data(sl)

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
