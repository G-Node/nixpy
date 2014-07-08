// Copyright (c) 2014, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE source in the root of the Project.

#include <boost/python.hpp>
#include <boost/optional.hpp>

#include <nix.hpp>

#include <accessors.hpp>
#include <transmorgify.hpp>

//we want only the newest and freshest API
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <numpy/arrayobject.h>
#include <numpy/ndarrayobject.h>

#include <PyEntity.hpp>

#include <stdexcept>

using namespace nix;
using namespace boost::python;

namespace nixpy {

// Label

void setLabel(DataArray& da, const boost::optional<std::string>& label) {
    if (label)
        da.label(*label);
    else
        da.label(boost::none);
}

// Unit

void setUnit(DataArray& da, const boost::optional<std::string> &unit) {
    if (unit)
        da.unit(*unit);
    else
        da.unit(boost::none);
}

// Expansion origin

void setExpansionOrigin(DataArray& da, const boost::optional<double>& eo) {
    if (eo)
        da.expansionOrigin(*eo);
    else
        da.expansionOrigin(boost::none);
}

// Polynom coefficients

void setPolynomCoefficients(DataArray& da, const std::vector<double>& pc) {
    if (!pc.empty())
        da.polynomCoefficients(pc);
    else
        da.polynomCoefficients(boost::none);
}

// Data

std::vector<double> getData(DataArray& da) {
    std::vector<double> data;
    da.getData(data);
    return data;
}

void setData(DataArray& da, const std::vector<double>& data) {
    if (!data.empty())
        da.setData(data);
    else
        // TODO How do I remove data?
        da.dataExtent(NDSize());
}

static nix::DataType py_dtype_to_nix_dtype(const PyArray_Descr *dtype)
{
    if (dtype == nullptr) {
        return nix::DataType::Nothing;
    }

    if (dtype->byteorder != '=' && dtype->byteorder != '|') {
        //TODO: Handle case where specified byteorder *is*
        //the native byteorder (via BOOST_BIG_ENDIAN macros)
        return nix::DataType::Nothing;
    }

    switch (dtype->kind) {

    case 'u':
        switch (dtype->elsize) {
        case 1: return nix::DataType::UInt8;
        case 2: return nix::DataType::UInt16;
        case 4: return nix::DataType::UInt32;
        case 8: return nix::DataType::UInt64;
        }
        break;

    case 'i':
        switch (dtype->elsize) {
        case 1: return nix::DataType::Int8;
        case 2: return nix::DataType::Int16;
        case 4: return nix::DataType::Int32;
        case 8: return nix::DataType::Int64;
        }
        break;

    case 'f':
        switch (dtype->elsize) {
        case 4: return nix::DataType::Float;
        case 8: return nix::DataType::Double;
        }
        break;

    default:
        break;
    }
    return nix::DataType::Nothing;
}

static nix::DataType array_desc_as_dtype(PyArrayObject *array) {
    nix::DataType nix_dtype = py_dtype_to_nix_dtype(PyArray_DESCR(array));

    if (nix_dtype == nix::DataType::Nothing) {
        throw std::invalid_argument("Unsupported dtype for data");
    }

    return nix_dtype;
}

static PyArrayObject *make_array(PyObject *data, int requirements) {
    if (! PyArray_Check(data)) {
        throw std::invalid_argument("Data not a NumPy array");
    }

    PyArrayObject *array = reinterpret_cast<PyArrayObject *>(data);

     if (! PyArray_CHKFLAGS(array, requirements)) {
        throw std::invalid_argument("data must be c-contiguous and aligned");
    }

     return array;
}

static NDSize array_shape_as_ndsize(PyArrayObject *array) {
    int array_rank = PyArray_NDIM(array);
    npy_intp *array_shape = PyArray_SHAPE(array);

    nix::NDSize data_shape(array_rank);
    for (int i = 0; i < array_rank; i++) {
        data_shape[i] = array_shape[i];
    }

    return data_shape;
}


static void readData(DataArray& da, PyObject *data) {

    PyArrayObject *array = make_array(data, NPY_ARRAY_CARRAY);

    nix::DataType nix_dtype = array_desc_as_dtype(array);
    nix::NDSize data_shape = array_shape_as_ndsize(array);
    nix::NDSize offset(data_shape.size(), 0);

    da.getData(nix_dtype, PyArray_DATA(array), data_shape, offset);
}


static void writeData(DataArray& da, PyObject *data) {

    PyArrayObject *array = make_array(data, NPY_ARRAY_CARRAY_RO);

    nix::DataType nix_dtype = array_desc_as_dtype(array);
    nix::NDSize data_shape = array_shape_as_ndsize(array);
    nix::NDSize offset(data_shape.size(), 0);

    da.setData(nix_dtype, PyArray_DATA(array), data_shape, offset);
}


static void createData(DataArray& da, const NDSize &shape, PyObject *dtype_obj, PyObject *data) {
    PyArray_Descr* py_dtype = nullptr;

    if (! PyArray_DescrConverter(dtype_obj, &py_dtype)) {
        throw std::invalid_argument("Invalid dtype");
    }

    nix::DataType nix_dtype = py_dtype_to_nix_dtype(py_dtype);
    if (nix_dtype == nix::DataType::Nothing) {
        throw std::invalid_argument("Unsupported dtype");
    }

    da.createData(nix_dtype, shape);

    if (data != Py_None) {
        writeData(da, data);
    }

    Py_DECREF(py_dtype);
}

// Dimensions

PyObject* getDimension(const DataArray& da, size_t index) {
    Dimension dim = da.getDimension(index);
    SetDimension set;
    RangeDimension range;
    SampledDimension sample;
    DimensionType type = dim.dimensionType();

    switch(type) {
        case DimensionType::Set:
            set = dim;
            return incref(object(set).ptr());
        case DimensionType::Range:
            range = dim;
            return incref(object(range).ptr());
        case DimensionType::Sample:
            sample = dim;
            return incref(object(sample).ptr());
        default:
            Py_RETURN_NONE;
    }
}

void PyDataArray::do_export() {

    // For numpy to work
    import_array();

    PyEntityWithSources<base::IDataArray>::do_export("DataArray");
    class_<DataArray, bases<base::EntityWithSources<base::IDataArray>>>("DataArray")
        .add_property("label",
                      OPT_GETTER(std::string, DataArray, label),
                      setLabel,
                      doc::data_array_label)
        .add_property("unit",
                      OPT_GETTER(std::string, DataArray, unit),
                      setUnit,
                      doc::data_array_unit)
        .add_property("expansion_origin",
                      OPT_GETTER(double, DataArray, expansionOrigin),
                      setExpansionOrigin,
                      doc::data_array_expansion_origin)
        .add_property("polynom_coefficients",
                      GETTER(std::vector<double>, DataArray, polynomCoefficients),
                      setPolynomCoefficients,
                      doc::data_array_polynom_coefficients)
        .add_property("data_extent",
                      GETTER(NDSize, DataArray, dataExtent),
                      SETTER(NDSize&, DataArray, dataExtent),
                      doc::data_array_data_extent)
        // Data
        .add_property("data_type", &DataArray::dataType,
                      doc::data_array_data_type)
        .add_property("data", getData, setData,
                      doc::data_array_data)
        .def("has_data", &DataArray::hasData,
                      doc::data_array_has_data)

        .def("_create_data", createData)
        .def("_write_data", writeData)
        .def("_read_data", readData)

        // Dimensions
        .def("create_set_dimension", &DataArray::createSetDimension,
             doc::data_array_create_set_dimension)
        .def("create_sampled_dimension", &DataArray::createSampledDimension,
             doc::data_array_create_sampled_dimension)
        .def("create_reange_dimension", &DataArray::createRangeDimension,
             doc::data_array_create_range_dimension)
        .def("append_set_dimension", &DataArray::appendSetDimension,
             doc::data_array_append_set_dimension)
        .def("append_sampled_dimension", &DataArray::appendSampledDimension,
             doc::data_array_append_sampled_dimension)
        .def("append_range_dimension", &DataArray::appendRangeDimension,
             doc::data_array_append_range_dimension)
        .def("_dimension_count", &DataArray::dimensionCount)
        .def("_delete_dimension_by_pos", &DataArray::deleteDimension)
        .def("_get_dimension_by_pos", getDimension)
        // Other
        .def("__str__", &toStr<DataArray>)
        .def("__repr__", &toStr<DataArray>)
        ;

    to_python_converter<std::vector<DataArray>, vector_transmogrify<DataArray>>();
    vector_transmogrify<DataArray>::register_from_python();

    to_python_converter<boost::optional<DataArray>, option_transmogrify<DataArray>>();
    option_transmogrify<DataArray>::register_from_python();
}

}
