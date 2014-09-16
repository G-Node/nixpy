# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest
import sys
import numpy as np

from nix import *

class TestDataArray(unittest.TestCase):

    def setUp(self):
        self.file  = File.open("unittest.h5", FileMode.Overwrite)
        self.block = self.file.create_block("test block", "recordingsession")
        self.array = self.block.create_data_array("test array", "signal", DataType.Double, (100, ))
        self.other = self.block.create_data_array("other array", "signal", DataType.Double, (100, ))

    def tearDown(self):
        del self.file.blocks[self.block.id]
        self.file.close()

    def test_data_array_eq(self):
        assert(self.array == self.array)
        assert(not self.array == self.other)
        assert(not self.array == None)

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
        self.array.data.write_direct(data)
        assert(self.array.data.dtype == np.dtype(float))
        self.array.data.read_direct(dout)
        assert(np.array_equal(data, dout))
        dout = np.array(self.array.data)
        assert(np.array_equal(data, dout))
        assert(self.array.data_extent == data.shape)
        assert(self.array.data_extent == self.array.data.shape)
        assert(self.array.data.size == data.size)

        assert(len(self.array.data) == len(data))

        #indexing support in 1-d arrays
        self.assertRaises(IndexError, lambda : self.array.data[1:4:5])
        self.assertRaises(IndexError, lambda : self.array.data[[1,3,]])

        dout = np.array([self.array.data[i] for i in range(100)])
        assert(np.array_equal(data, dout))

        dout = self.array.data[...]
        assert(np.array_equal(data, dout))

        #indexed writing (1-d)
        data = np.array([float(-i) for i in range(100)])
        self.array.data[()] = data
        assert(np.array_equal(self.array.data[...], data))

        self.array.data[...] = [float(-i) for i in range(100)]
        assert(np.array_equal(self.array.data[()], data))

        self.array.data[0] = 42
        assert(self.array.data[0] == 42.0)

        #changing shape via data_extent property
        self.array.data_extent = (200, )
        assert(self.array.data_extent == (200, ))

        # TODO delete does not work
        data = np.eye(123)
        a1 = self.block.create_data_array("double array", "signal", DataType.Double, (123, 123))
        dset = a1.data
        dset.write_direct(data)
        dout = np.empty_like(data)
        dset.read_direct(dout)
        assert(np.array_equal(data, dout))

        #indexing support in 2-d arrays
        self.assertRaises(IndexError, lambda : self.array.data[[], [1,2]])

        dout = dset[12]
        assert(dout.shape == data[12].shape)
        assert(np.array_equal(dout, data[12]))
        assert(np.array_equal(dset[()], data))
        assert(np.array_equal(dset[...], data))
        assert(np.array_equal(dset[12, ...], data[12, ...]))
        assert(np.array_equal(dset[..., 12], data[..., 12]))
        assert(np.array_equal(dset[1:], data[1:]))
        assert(np.array_equal(dset[:1], data[:1]))
        assert(np.array_equal(dset[1:10, 1:10], data[1:10, 1:10]))

        a3 = self.block.create_data_array("int identity array", "signal", DataType.Int32, (123, 123))
        assert(a3.data_extent == (123, 123))
        assert(a3.data.dtype == np.dtype('i4'))

        data = np.random.rand(3, 4, 5)
        a4 = self.block.create_data_array("3d array", "signal", DataType.Double, (3, 4, 5))
        dset = a4.data
        dset.write_direct(data)
        assert(dset.shape == data.shape)
        assert(len(dset) == len(data))
        assert(dset.size == data.size)
        assert(np.array_equal(dset[2, ...], data[2, ...]))
        assert(np.array_equal(dset[..., 3], data[..., 3]))
        assert(np.array_equal(dset[2, ..., 3], data[2, ..., 3]))
        assert(np.array_equal(dset[1:2, ..., 3:5], data[1:2, ..., 3:5]))

        #indexed writing (n-d)
        d2 = np.random.rand(2,2)
        dset[1, 0:2, 0:2] = d2
        assert(np.array_equal(dset[1, 0:2, 0:2], d2))

        # test for the size check in DataSet.__len__
        # by simulating a system with a really smal int
        savemaxsize = sys.maxsize
        sys.maxsize = len(dset) - 1
        self.assertRaises(OverflowError, lambda : len(dset))
        sys.maxsize = savemaxsize

        # test inferring shape & dtype from data, and writing the data
        test_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], dtype=int)
        da = self.block.create_data_array('created_from_data', 'b', data=test_data)
        assert(da.data.shape == test_data.shape)
        assert(np.array_equal(test_data, da.data[:]))

        #test for exceptions
        self.assertRaises(ValueError, lambda: self.block.create_data_array('x', 'y'))
        self.assertRaises(ValueError, lambda: self.block.create_data_array('x', 'y', data=test_data, shape=(1, 1, 1)))

    def test_data_array_dtype(self):
        da = self.block.create_data_array('dtype_f8', 'b', 'f8', (10, 10))
        assert(da.data.dtype == np.dtype('f8'))

        da = self.block.create_data_array('dtype_i16', 'b', np.int16, (10, 10))
        data = da.data[:]
        assert(da.data.dtype == np.int16)
        assert(data.dtype == np.int16)

        da = self.block.create_data_array('dtype_int', 'b', int, (10, 10))
        assert(da.data.dtype == np.dtype(int))

        da = self.block.create_data_array('dtype_ndouble', 'b', DataType.Double, (10, 10))
        assert(da.data.dtype == np.dtype('f8'))

        da = self.block.create_data_array('dtype_auto', 'b', None, (10, 10))
        assert(da.data.dtype == np.dtype('f8'))

        test_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], dtype=int)
        da = self.block.create_data_array('dtype_int_from_data', 'b', data=test_data)
        assert(da.data.dtype == test_data.dtype)

        void_data = np.array(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'], dtype='V1')
        da = self.block.create_data_array('dtype_opaque', 'b', data=void_data)
        assert(da.data.dtype == np.dtype('V1'))
        assert(np.array_equal(void_data, da.data[:]))

    def test_data_array_dimensions(self):
        assert(len(self.array.dimensions) == 0)

        setd    = self.array.append_set_dimension()
        ranged  = self.array.append_range_dimension(range(10))
        sampled = self.array.append_sampled_dimension(0.1)

        assert(len(self.array.dimensions) == 3)

        self.assertRaises(TypeError, lambda : self.array.dimensions["notexist"])
        self.assertRaises(KeyError, lambda : self.array.dimensions[-4])
        self.assertRaises(KeyError, lambda : self.array.dimensions[3])

        assert(isinstance(str(self.array.dimensions), basestring))
        assert(isinstance(repr(self.array.dimensions), basestring))

        dims   = list(self.array.dimensions)
        for i in range(3):
            assert(dims[i].index == self.array.dimensions[i].index)
            assert(dims[i].dimension_type == self.array.dimensions[i].dimension_type)

            assert(self.array.dimensions[i].index == self.array.dimensions[i - 3].index)

        del self.array.dimensions[2]
        del self.array.dimensions[1]
        del self.array.dimensions[0]

        assert(len(self.array.dimensions) == 0)

    def test_data_array_sources(self):
        source1 = self.block.create_source("source1", "channel")
        source2 = self.block.create_source("source2", "electrode")

        assert(len(self.array.sources) == 0)

        self.array.sources.append(source1)
        self.array.sources.append(source2)

        self.assertRaises(TypeError, lambda : self.array.sources.append(100))

        assert(len(self.array.sources) == 2)
        assert(source1 in self.array.sources)
        assert(source2 in self.array.sources)

        del self.array.sources[source2]
        assert(self.array.sources[0] == source1)

        del self.array.sources[source1]
        assert(len(self.array.sources) == 0)
