# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import numpy as np


class DataSet:
    """
    Data IO object for DataArray.
    """

    def __array__(self):
        return self._read_data()[:]

    def __getitem__(self, index):
        return self._read_data(index)

    def __setitem__(self, index, value):
        self._write_data(value, index)

    def __len__(self):
        return self.len()

    def __iter__(self):
        for idx in range(self.len()):
            yield self[idx]

    def len(self):
        """
        Length of the first dimension. Equivalent to `DataSet.shape[0]`.

        :type: int or long
        """
        return self.shape[0]

    @property
    def shape(self):
        """
        :type: tuple of data array dimensions.
        """
        return self.data_extent

    @property
    def size(self):
        """
        Number of elements in the DataSet, i.e. the product of the
        elements in :attr:`~nixio.data_array.DataSet.shape`.

        :type: int
        """
        return np.prod(self.shape)

    @property
    def dtype(self):
        """
        :type: :class:`numpy.dtype` object holding type information about
               the data stored in the DataSet.
        """
        return np.dtype(self._get_dtype())

    def write_direct(self, data):
        """
        Directly write all of ``data`` to the
        :class:`~nixio.data_array.DataSet`.  The supplied data must be a
        :class:`numpy.ndarray` that matches the DataSet's shape and must have
        C-style contiguous memory layout (see :attr:`numpy.ndarray.flags` and
        :class:`~numpy.ndarray` for more information).

        :param data: The array which contents is being written
        :type data: :class:`numpy.ndarray`
        """
        self._write_data(data)

    def read_direct(self, data):
        """
        Directly read all data stored in the :class:`~nixio.data_array.DataSet`
        into ``data``. The supplied data must be a :class:`numpy.ndarray` that
        matches the DataSet's shape, must have C-style contiguous memory layout
        and must be writeable (see :attr:`numpy.ndarray.flags` and
        :class:`~numpy.ndarray` for more information).

        :param data: The array where data is being read into
        :type data: :class:`numpy.ndarray`
        """
        data[:] = self._read_data()

    def append(self, data, axis=0):
        """
        Append ``data`` to the DataSet along the ``axis`` specified.

        :param data: The data to append. Shape must agree except for the
                     specified axis
        :param axis: Along which axis to append the data to
        """
        data = np.ascontiguousarray(data)
        if len(self.shape) != len(data.shape):
            raise ValueError(
                "Data and DataArray must have the same dimensionality"
            )

        if any([s != ds for i, (s, ds) in
                enumerate(zip(self.shape, data.shape)) if i != axis]):
            raise ValueError("Shape of data and shape of DataArray must match "
                             "in all dimension but axis!")

        offset = tuple(0 if i != axis else x for i, x in enumerate(self.shape))
        count = data.shape
        enlarge = tuple(self.shape[i] + (0 if i != axis else x)
                        for i, x in enumerate(data.shape))
        self.data_extent = enlarge
        slc = tuple(slice(o, c+o) for o, c in zip(offset, count))
        self._write_data(data, slc)

    def _write_data(self, data, slc=None):
        dataset = self._h5group.get_dataset("data")
        dataset.write_data(data,  slc)

    def _read_data(self, slc=None):
        return self._h5group.get_dataset("data").read_data(slc)

    @property
    def data_extent(self):
        """
        The size of the data.

        :type: tuple of int
        """
        dataset = self._h5group.get_dataset("data")
        return dataset.shape

    @data_extent.setter
    def data_extent(self, extent):
        dataset = self._h5group.get_dataset("data")
        dataset.shape = extent

    @property
    def data_type(self):
        """
        The data type of the data stored in the DataArray. This is a read only
        property.

        :type: nixio.DataType
        """
        return self._get_dtype()

    def _get_dtype(self):
        dataset = self._h5group.get_dataset("data")
        return dataset.dtype
