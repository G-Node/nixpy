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

static nix::DataType pyDtypeToNixDtype(const PyArray_Descr *dtype)
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

    case 'V':
        return nix::DataType::Opaque;
        //we are ignoring the size information here
        //since we only support NATIVE_OPAQUE in H5
        //maybe we should throw an exception instead
        break;

    default:
        break;
    }
    return nix::DataType::Nothing;
}

static std::string nixDtypeToPyDtypeStr(nix::DataType nix_dtype)
{
    switch (nix_dtype) {
    case nix::DataType::UInt8:  return "<u1";
    case nix::DataType::UInt16: return "<u2";
    case nix::DataType::UInt32: return "<u4";
    case nix::DataType::UInt64: return "<u8";
    case nix::DataType::Int8:   return "<i1";
    case nix::DataType::Int16:  return "<i2";
    case nix::DataType::Int32:  return "<i4";
    case nix::DataType::Int64:  return "<i8";
    case nix::DataType::Float:  return "<f4";
    case nix::DataType::Double: return "<f8";
    case nix::DataType::Opaque: return "|V1";
    default:                    return "";
    }
}

static nix::DataType arrayDescAsDtype(PyArrayObject *array) {
    nix::DataType nix_dtype = pyDtypeToNixDtype(PyArray_DESCR(array));

    if (nix_dtype == nix::DataType::Nothing) {
        throw std::invalid_argument("Unsupported dtype for data");
    }

    return nix_dtype;
}

static PyArrayObject *makeArray(PyObject *data, int requirements) {
    if (! PyArray_Check(data)) {
        throw std::invalid_argument("Data not a NumPy array");
    }

    PyArrayObject *array = reinterpret_cast<PyArrayObject *>(data);
    PyArray_Descr *descr = PyArray_DESCR(array);

    if (requirements & NPY_ARRAY_ALIGNED && descr->kind == 'V') {
       //workaround a strange behaviour of numpy 1.9 to return
       //is_aligned == FALSE for void datatypes with an alignment
       //requirement == 1
       if (descr->alignment == 1) {
          requirements &= ~NPY_ARRAY_ALIGNED;
       }
    }

     if (! PyArray_CHKFLAGS(array, requirements)) {
        throw std::invalid_argument("array does not meet requirements");
    }

     return array;
}

static NDSize arrayShapeAsNDSize(PyArrayObject *array) {
    int array_rank = PyArray_NDIM(array);
    npy_intp *array_shape = PyArray_SHAPE(array);

    nix::NDSize data_shape(array_rank);
    for (int i = 0; i < array_rank; i++) {
        data_shape[i] = array_shape[i];
    }

    return data_shape;
}


static void arrayEnsureShapeAndCount(PyArrayObject *array,
                                         nix::NDSize    count,
                                         nix::NDSize    offset) {

    if (! count) {
        count = arrayShapeAsNDSize(array);
    }

    if (! offset) {
        offset = nix::NDSize(count.size(), 0);
    }
}


static void readData(DataArray& da, PyObject *data, nix::NDSize count, nix::NDSize offset) {

    PyArrayObject *array = makeArray(data, NPY_ARRAY_CARRAY);

    nix::DataType nix_dtype = arrayDescAsDtype(array);

    arrayEnsureShapeAndCount(array, count, offset);
    da.getData(nix_dtype, PyArray_DATA(array), count, offset);
}


static void writeData(DataArray& da, PyObject *data, nix::NDSize count, nix::NDSize offset) {

    PyArrayObject *array = makeArray(data, NPY_ARRAY_CARRAY_RO);

    nix::DataType nix_dtype = arrayDescAsDtype(array);

    arrayEnsureShapeAndCount(array, count, offset);
    da.setData(nix_dtype, PyArray_DATA(array), count, offset);
}


static std::string getDataType(const DataArray& da)
{
    nix::DataType nix_dtype = da.dataType();
    return nixDtypeToPyDtypeStr(nix_dtype);
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

//

struct dtype_transmogrify {
    typedef boost::python::converter::rvalue_from_python_stage1_data py_s1_data;
    typedef boost::python::converter::rvalue_from_python_storage<nix::DataType> py_storage;

       // PyObject* -> nix::DataType
    static void register_from_python() {
        boost::python::converter::registry::push_back(is_convertible,
                                                      construct,
                                                      boost::python::type_id<nix::DataType>());
    }

    static void* is_convertible(PyObject *obj) {
        namespace bp = boost::python;

        PyArray_Descr* py_dtype = nullptr;

        if (! PyArray_DescrConverter(obj, &py_dtype)) {
            // PyArray_DescrConverter will have set an TypeError
            // exception if this occurs, clear it
            PyErr_Clear();
            return nullptr;
        }

        Py_DECREF(py_dtype);
        return obj;
    }

    static void construct(PyObject *obj, py_s1_data *data) {
        namespace bp = boost::python;

        void *raw = static_cast<void *>(reinterpret_cast<py_storage *>(data)->storage.bytes);

        PyArray_Descr* py_dtype = nullptr;
        //should work, because we checked with is_convertible
        PyArray_DescrConverter(obj, &py_dtype);

        nix::DataType * const dtype_ptr = static_cast<nix::DataType *>(raw);
        *dtype_ptr = pyDtypeToNixDtype(py_dtype);
        data->convertible = raw;
    }

};


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
        .def("_write_data", writeData)
        .def("_read_data", readData)
        .def("_get_dtype", getDataType)

        // Dimensions
        .def("create_set_dimension", &DataArray::createSetDimension,
             doc::data_array_create_set_dimension)
        .def("create_sampled_dimension", &DataArray::createSampledDimension,
             doc::data_array_create_sampled_dimension)
        .def("create_range_dimension", &DataArray::createRangeDimension,
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

    dtype_transmogrify::register_from_python();
}

}
