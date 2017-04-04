# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)

import unittest
import sys
import numpy as np

import nixio as nix
try:
    nix.core
    skip_cpp = False
except AttributeError:
    skip_cpp = True

try:
    basestring = basestring
except NameError:  # 'basestring' is undefined, must be Python 3
    basestring = (str, bytes)


class _TestDataArray(unittest.TestCase):

    backend = None

    def setUp(self):
        self.file = nix.File.open("unittest.h5", nix.FileMode.Overwrite,
                                  backend=self.backend)
        self.block = self.file.create_block("test block", "recordingsession")
        self.array = self.block.create_data_array("test array", "signal",
                                                  nix.DataType.Double, (100, ))
        self.other = self.block.create_data_array("other array", "signal",
                                                  nix.DataType.Double, (100, ))

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()

    def test_data_array_eq(self):
        assert(self.array == self.array)
        assert(not self.array == self.other)
        assert(self.array is not None)

    def test_data_array_id(self):
        assert(self.array.id is not None)

    def test_data_array_name(self):
        assert(self.array.name is not None)

    def test_data_array_type(self):
        def set_none():
            self.array.type = None

        assert(self.array.type is not None)
        self.assertRaises(Exception, set_none)

        self.array.type = "foo type"
        assert(self.array.type == "foo type")

    def test_data_array_definition(self):
        assert(self.array.definition is None)

        self.array.definition = "definition"
        assert(self.array.definition == "definition")

        self.array.definition = None
        assert(self.array.definition is None)

    def test_data_array_timestamps(self):
        created_at = self.array.created_at
        assert(created_at > 0)

        updated_at = self.array.updated_at
        assert(updated_at > 0)

        self.array.force_created_at(1403530068)
        assert(self.array.created_at == 1403530068)

    def test_data_array_label(self):
        assert(self.array.label is None)

        self.array.label = "label"
        assert(self.array.label == "label")

        self.array.label = None
        assert(self.array.label is None)

    def test_data_array_unit(self):
        assert(self.array.unit is None)

        self.array.unit = "mV"
        assert(self.array.unit == "mV")

        self.array.unit = None
        assert(self.array.unit is None)

    def test_data_array_exp_origin(self):
        assert(self.array.expansion_origin is None)

        self.array.expansion_origin = 10.2
        assert(self.array.expansion_origin == 10.2)

        self.array.expansion_origin = None
        assert(self.array.expansion_origin is None)

    def test_data_array_coefficients(self):
        assert(self.array.polynom_coefficients == ())

        self.array.polynom_coefficients = (1.1, 2.2)
        assert(self.array.polynom_coefficients == (1.1, 2.2))

        # TODO delete does not work

    def test_data_array_data(self):

        assert(self.array.polynom_coefficients == ())

        data = np.array([float(i) for i in range(100)])
        dout = np.empty_like(data)
        self.array.write_direct(data)
        assert(self.array.dtype == np.dtype(float))
        self.array.read_direct(dout)
        assert(np.array_equal(data, dout))
        dout = np.array(self.array)
        assert(np.array_equal(data, dout))
        assert(self.array.data_extent == data.shape)
        assert(self.array.data_extent == self.array.shape)
        assert(self.array.size == data.size)

        assert(len(self.array) == len(data))

        # indexing support in 1-d arrays
        self.assertRaises(IndexError, lambda: self.array[1:4:5])
        self.assertRaises(IndexError, lambda: self.array[[1, 3, ]])

        dout = np.array([self.array[i] for i in range(100)])
        assert(np.array_equal(data, dout))

        dout = self.array[...]
        assert(np.array_equal(data, dout))

        # indexed writing (1-d)
        data = np.array([float(-i) for i in range(100)])
        self.array[()] = data
        assert(np.array_equal(self.array[...], data))

        self.array[...] = [float(-i) for i in range(100)]
        assert(np.array_equal(self.array[()], data))
        assert(np.array_equal(self.array[0:-10], data[0:-10]))
        assert(np.array_equal(self.array[-10], data[-10]))

        self.array[0] = 42
        assert(self.array[0] == 42.0)

        # changing shape via data_extent property
        self.array.data_extent = (200, )
        assert(self.array.data_extent == (200, ))

        # TODO delete does not work
        data = np.eye(123)
        a1 = self.block.create_data_array("double array", "signal",
                                          nix.DataType.Double, (123, 123))
        dset = a1
        dset.write_direct(data)
        dout = np.empty_like(data)
        dset.read_direct(dout)
        assert(np.array_equal(data, dout))

        # indexing support in 2-d arrays
        self.assertRaises(IndexError, lambda: self.array[[], [1, 2]])

        dout = dset[12]
        assert(dout.shape == data[12].shape)
        assert(np.array_equal(dout, data[12]))
        assert(np.array_equal(dset[()], data))
        assert(np.array_equal(dset[...], data))
        assert(np.array_equal(dset[12, ...], data[12, ...]))
        assert(np.array_equal(dset[..., 12], data[..., 12]))
        assert(np.array_equal(dset[1:], data[1:]))
        assert(np.array_equal(dset[-20:, -20:], data[123-20:, 123-20:]))
        assert(np.array_equal(dset[:1], data[:1]))
        assert(np.array_equal(dset[:-1, :-1], data[1:123, 1:123]))
        assert(np.array_equal(dset[1:10, 1:10], data[1:10, 1:10]))
        assert(np.array_equal(dset[1:-2, 1:-2], data[1:121, 1:121]))

        a3 = self.block.create_data_array("int identity array", "signal",
                                          nix.DataType.Int32, (123, 123))
        assert(a3.shape == (123, 123))
        assert(a3.dtype == np.dtype('i4'))

        data = np.random.rand(3, 4, 5)
        a4 = self.block.create_data_array("3d array", "signal",
                                          nix.DataType.Double, (3, 4, 5))
        dset = a4
        dset.write_direct(data)
        assert(dset.shape == data.shape)
        assert(len(dset) == len(data))
        assert(dset.size == data.size)
        assert(np.array_equal(dset[2, ...], data[2, ...]))
        assert(np.array_equal(dset[-1, ...], data[2, ...]))
        assert(np.array_equal(dset[..., 3], data[..., 3]))
        assert(np.array_equal(dset[..., -2], data[..., 3]))
        assert(np.array_equal(dset[2, ..., 3], data[2, ..., 3]))
        assert(np.array_equal(dset[2, ..., -2], data[2, ..., 3]))
        assert(np.array_equal(dset[1:2, ..., 3:5], data[1:2, ..., 3:5]))
        assert(np.array_equal(dset[1:2, ..., 3:-1], data[1:2, ..., 3:4]))

        # indexed writing (n-d)
        d2 = np.random.rand(2, 2)
        dset[1, 0:2, 0:2] = d2
        assert(np.array_equal(dset[1, 0:2, 0:2], d2))

        # test for the size check in DataSet.__len__
        # by simulating a system with a really smal int
        savemaxsize = sys.maxsize
        sys.maxsize = len(dset) - 1
        self.assertRaises(OverflowError, lambda: len(dset))
        sys.maxsize = savemaxsize

        # test inferring shape & dtype from data, and writing the data
        test_ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        test_data = np.array(test_ten, dtype=int)
        da = self.block.create_data_array('created_from_data', 'b',
                                          data=test_data)
        assert(da.shape == test_data.shape)
        assert(np.array_equal(test_data, da[:]))
        assert(test_ten == [x for x in da])

        # test for exceptions
        self.assertRaises(ValueError,
                          lambda: self.block.create_data_array('x', 'y'))
        self.assertRaises(ValueError,
                          lambda: self.block.create_data_array(
                              'x', 'y', data=test_data, shape=(1, 1, 1)
                          ))

        # test appending
        data = np.zeros((10, 5))
        da = self.block.create_data_array('append', 'double', data=data)
        to_append = np.zeros((2, 5))

        da.append(to_append)
        assert(da.shape == (12, 5))

        to_append = np.zeros((12, 2))
        da.append(to_append, axis=1)
        assert(da.shape == (12, 7))

        self.assertRaises(ValueError, lambda: da.append(np.zeros((3, 3, 3))))
        self.assertRaises(ValueError, lambda: da.append(np.zeros((5, 5))))

    def test_data_array_dtype(self):
        da = self.block.create_data_array('dtype_f8', 'b', 'f8', (10, 10))
        assert(da.dtype == np.dtype('f8'))

        da = self.block.create_data_array('dtype_i16', 'b', np.int16, (10, 10))
        data = da[:]
        assert(da.dtype == np.int16)
        assert(data.dtype == np.int16)

        da = self.block.create_data_array('dtype_int', 'b', int, (10, 10))
        assert(da.dtype == np.dtype(int))

        da = self.block.create_data_array('dtype_ndouble', 'b',
                                          nix.DataType.Double, (10, 10))
        assert(da.dtype == np.dtype('f8'))

        da = self.block.create_data_array('dtype_auto', 'b', None, (10, 10))
        assert(da.dtype == np.dtype('f8'))

        test_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], dtype=int)
        da = self.block.create_data_array('dtype_int_from_data', 'b',
                                          data=test_data)
        assert(da.dtype == test_data.dtype)

        bdata = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        if sys.version_info[0] == 3:
            bdata = [bytes(x, 'UTF-8') for x in bdata]

        void_data = np.array(bdata, dtype='V1')
        da = self.block.create_data_array('dtype_opaque', 'b', data=void_data)
        assert(da.dtype == np.dtype('V1'))
        assert(np.array_equal(void_data, da[:]))

    def test_data_array_dimensions(self):
        assert(len(self.array.dimensions) == 0)

        self.array.append_set_dimension()
        self.array.append_range_dimension(range(10))
        self.array.append_sampled_dimension(0.1)

        assert(len(self.array.dimensions) == 3)

        self.assertRaises(TypeError, lambda: self.array.dimensions["notexist"])
        self.assertRaises(KeyError, lambda: self.array.dimensions[-4])
        self.assertRaises(KeyError, lambda: self.array.dimensions[3])

        assert(isinstance(str(self.array.dimensions), basestring))
        assert(isinstance(repr(self.array.dimensions), basestring))

        dims = list(self.array.dimensions)
        for i in range(3):
            assert(dims[i].index == self.array.dimensions[i].index)
            assert(dims[i].dimension_type ==
                   self.array.dimensions[i].dimension_type)

            assert(self.array.dimensions[i].index ==
                   self.array.dimensions[i-3].index)

        self.array.delete_dimensions()

        assert(len(self.array.dimensions) == 0)
        self.array.append_alias_range_dimension()
        assert(len(self.array.dimensions) == 1)
        self.array.delete_dimensions()
        self.array.append_alias_range_dimension()
        assert(len(self.array.dimensions) == 1)

        self.assertRaises(ValueError,
                          lambda: self.array.append_alias_range_dimension())
        self.assertRaises(ValueError,
                          lambda: self.array.append_alias_range_dimension())
        string_array = self.block.create_data_array('string_array',
                                                    'nix.texts',
                                                    dtype=nix.DataType.String,
                                                    shape=(10,))
        self.assertRaises(ValueError,
                          lambda: string_array.append_alias_range_dimension())
        assert(len(string_array.dimensions) == 0)
        del self.block.data_arrays['string_array']

        array_2D = self.block.create_data_array(
            'array_2d', 'nix.2d', dtype=nix.DataType.Double, shape=(10, 10)
        )
        self.assertRaises(ValueError,
                          lambda: array_2D.append_alias_range_dimension())
        assert(len(array_2D.dimensions) == 0)
        del self.block.data_arrays['array_2d']

    def test_data_array_sources(self):
        source1 = self.block.create_source("source1", "channel")
        source2 = self.block.create_source("source2", "electrode")

        assert(len(self.array.sources) == 0)

        self.array.sources.append(source1)
        self.array.sources.append(source2)

        self.assertRaises(TypeError, lambda: self.array.sources.append(100))

        assert(len(self.array.sources) == 2)
        assert(source1 in self.array.sources)
        assert(source2 in self.array.sources)

        del self.array.sources[source2]
        assert(self.array.sources[0] == source1)

        del self.array.sources[source1]
        assert(len(self.array.sources) == 0)


@unittest.skipIf(skip_cpp, "HDF5 backend not available.")
class TestDataArrayCPP(_TestDataArray):

    backend = "hdf5"


class TestDataArrayPy(_TestDataArray):

    backend = "h5py"
