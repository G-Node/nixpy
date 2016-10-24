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

namespace nixpy {

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

    case 'S':
        return nix::DataType::String;
        break;

    case 'b':
        return nix::DataType::Bool;
        break;

    default:
        break;
    }
    return nix::DataType::Nothing;
}

static std::string nixDtypeToPyDtypeStr(nix::DataType nix_dtype)
{
    switch (nix_dtype) {
        case nix::DataType::Bool:   return "<b1";
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

static nix::NDSize arrayShapeAsNDSize(PyArrayObject *array) {
    int array_rank = PyArray_NDIM(array);
    npy_intp *array_shape = PyArray_SHAPE(array);

    nix::NDSize data_shape(array_rank);
    for (int i = 0; i < array_rank; i++) {
        data_shape[i] = array_shape[i];
    }

    return data_shape;
}


static void arrayEnsureShapeAndCount(PyArrayObject *array,
                                     nix::NDSize    &count,
                                     nix::NDSize    &offset) {

    if (! count) {
        count = arrayShapeAsNDSize(array);
    }

    if (! offset) {
        offset = nix::NDSize(count.size(), 0);
    }
}


static void readData(nix::DataSet& da, PyObject *data, nix::NDSize count, nix::NDSize offset) {

    PyArrayObject *array = makeArray(data, NPY_ARRAY_CARRAY);

    nix::DataType nix_dtype = arrayDescAsDtype(array);

    arrayEnsureShapeAndCount(array, count, offset);
    da.getData(nix_dtype, PyArray_DATA(array), count, offset);
}


static void writeData(nix::DataSet& da, PyObject *data, nix::NDSize count, nix::NDSize offset) {

    PyArrayObject *array = makeArray(data, NPY_ARRAY_CARRAY_RO);

    nix::DataType nix_dtype = arrayDescAsDtype(array);

    arrayEnsureShapeAndCount(array, count, offset);
    da.setData(nix_dtype, PyArray_DATA(array), count, offset);
}


static std::string getDataType(const nix::DataSet& da)
{
    nix::DataType nix_dtype = da.dataType();
    return nixDtypeToPyDtypeStr(nix_dtype);
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

    static PyObject* convert(const nix::DataType& dtype) {
        PyObject* module = PyImport_ImportModule("nixio.value");
        if (!module) return NULL;
        static PyObject* PyDataType = PyObject_GetAttrString(module, "DataType");
        std::string type_str;

        switch(dtype) {
            case nix::DataType::Bool:
                type_str = "Bool";
                break;
            case nix::DataType::Float:
                type_str = "Float";
                break;
            case nix::DataType::Double:
                type_str = "Double";
                break;
            case nix::DataType::Int8:
                type_str = "Int8";
                break;
            case nix::DataType::Int16:
                type_str = "Int16";
                break;
            case nix::DataType::Int32:
                type_str = "Int32";
                break;
            case nix::DataType::Int64:
                type_str = "Int64";
                break;
            case nix::DataType::UInt8:
                type_str = "UInt8";
                break;
            case nix::DataType::UInt16:
                type_str = "UInt16";
                break;
            case nix::DataType::UInt32:
                type_str = "UInt32";
                break;
            case nix::DataType::UInt64:
                type_str = "UInt64";
                break;
            case nix::DataType::Char:
            case nix::DataType::String:
                type_str = "String";
                break;
            // Missing: Nothing and Opaque
        }
        return PyObject_GetAttrString(PyDataType, type_str.c_str());
    }

};

struct DataSetWrapper : public nix::DataSet, public boost::python::wrapper<nix::DataSet> {

    void ioRead(nix::DataType dtype,
                void *data,
                const nix::NDSize &count,
                const nix::NDSize &offset) const {
        const boost::python::override fn = this->get_override("ioRead");
        fn(dtype, static_cast<char*>(data), std::ref(count), std::ref(offset));
    }

     void ioWrite(nix::DataType dtype,
                  const void *data,
                  const nix::NDSize &count,
                  const nix::NDSize &offset) {
        const boost::python::override fn = this->get_override("ioWrite");
        fn(dtype, static_cast<const char*>(data), std::ref(count), std::ref(offset));
     }
     virtual void dataExtent(const nix::NDSize &extent) override {
        this->get_override("dataExtent")(extent);
     }

     virtual nix::NDSize dataExtent() const override {
        return this->get_override("dataExtent")();
     };

     virtual nix::DataType dataType() const override {
        return this->get_override("dataType")();
     }
};

NIXPY_DO_EXPORT_RETTYPE PyDataSet::do_export() {
    using namespace boost::python;

    // For numpy to work
    import_array();

    class_<DataSetWrapper, boost::noncopyable>("DataSet")
        .def("_write_data", writeData)
        .def("_read_data", readData)
        .def("_get_dtype", getDataType)
        .add_property("data_extent",
                      GETTER(nix::NDSize, nix::DataSet, dataExtent),
                      SETTER(nix::NDSize&, nix::DataSet, dataExtent),
                      doc::data_array_data_extent)
        .add_property("data_type", &nix::DataSet::dataType,
                      doc::data_array_data_type);


    class_<nix::DataView, bases<nix::DataSet>>("DataView", boost::python::no_init);

    to_python_converter<nix::DataType, dtype_transmogrify>();
    dtype_transmogrify::register_from_python();

    return NIXPY_DO_EXPORT_RETVAL;
}

} // nixpy::
