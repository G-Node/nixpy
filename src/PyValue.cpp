// Copyright (c) 2014, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE file in the root of the Project.

#include <boost/python.hpp>
#include <boost/optional.hpp>

#include <nix.hpp>
#include <accessors.hpp>
#include <transmorgify.hpp>

#include <PyEntity.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {


boost::shared_ptr<Value> create(PyObject* value) {

    boost::shared_ptr<Value> created = boost::shared_ptr<Value>(new Value());

    if (PyBool_Check(value)) {
        bool conv = extract<bool>(value);
        created->set(conv);
#if PY_MAJOR_VERSION >= 3
    } else if (PyLong_Check(value)) {
#else
    } else if (PyInt_Check(value)) {
#endif
        int64_t conv = extract<int64_t>(value);
        created->set(conv);
    } else if (PyFloat_Check(value)) {
        double conv = extract<double>(value);
        created->set(conv);
#if PY_MAJOR_VERSION >= 3
    } else if (PyUnicode_Check(value)) {
#else
    } else if (PyString_Check(value)) {
#endif
        std::string conv = extract<std::string>(value);
        created->set(conv);
    } else {
        throw std::runtime_error("Wrong type");
    }

    return created;
}

void set(Value& ref, PyObject* value) {

    if (value == Py_None) {
        ref.set(boost::none);
    } else if (PyBool_Check(value)) {
        bool conv = extract<bool>(value);
        ref.set(conv);
#if PY_MAJOR_VERSION >= 3
    } else if (PyLong_Check(value)) {
#else
    } else if (PyInt_Check(value)) {
#endif
        int64_t conv = extract<int64_t>(value);
        ref.set(conv);
    } else if (PyFloat_Check(value)) {
        double conv = extract<double>(value);
        ref.set(conv);
#if PY_MAJOR_VERSION >= 3
    } else if (PyUnicode_Check(value)) {
#else
    } else if (PyString_Check(value)) {
#endif
        std::string conv = extract<std::string>(value);
        ref.set(conv);
    } else {
        throw std::runtime_error("Wrong type");
    }

}

PyObject* get(const Value& ref) {

    DataType type = ref.type();
    switch(type) {
        case DataType::Bool:
            return incref(object(ref.get<bool>()).ptr());
        case DataType::Float:
        case DataType::Double:
            return incref(object(ref.get<double>()).ptr());
        case DataType::Char:
        case DataType::Int8:
        case DataType::Int16:
        case DataType::Int32:
        case DataType::Int64:
            return incref(object(ref.get<int64_t>()).ptr());
        case DataType::UInt8:
        case DataType::UInt16:
        case DataType::UInt32:
        case DataType::UInt64:
            return incref(object(ref.get<uint64_t>()).ptr());
        case DataType::String:
            return incref(object(ref.get<std::string>()).ptr());
        case DataType::Nothing:
        default:
            Py_RETURN_NONE;
    }
}



static nix::Value pyValuetoNixValue(PyObject* obj) {
    PyObject* pyvalue = PyObject_GetAttrString(obj, "value");
    PyObject* pytype = PyObject_GetAttrString(obj, "data_type");
    std::string tname = extract<std::string>(PyObject_GetAttrString(pytype, "__name__"));

    if (tname == "uint8") {
        return nix::Value(extract<uint8_t>(pyvalue));
    } else if (tname == "uint16") {
        return nix::Value(extract<uint16_t>(pyvalue));
    } else if (tname == "uint32") {
        return nix::Value(extract<uint32_t>(pyvalue));
    } else if (tname == "uint64") {
        return nix::Value(extract<uint64_t>(pyvalue));
    } else if (tname == "int8") {
        return nix::Value(extract<int8_t>(pyvalue));
    } else if (tname == "int16") {
        return nix::Value(extract<int16_t>(pyvalue));
    } else if (tname == "int32") {
        return nix::Value(extract<int32_t>(pyvalue));
    } else if (tname == "int64") {
        return nix::Value(extract<uint64_t>(pyvalue));
    } else if (tname == "bytes_" || tname == "string_") {
        return nix::Value(extract<std::string>(pyvalue));
    } else if (tname == "bool_") {
        return nix::Value(extract<bool>(pyvalue));
    } else if (tname == "float32") {
        return nix::Value(extract<float>(pyvalue));
    } else if (tname == "float64") {
        return nix::Value(extract<double>(pyvalue));
    } else {
        // TODO: Error
    }
}

struct value_transmogrify {
    typedef boost::python::converter::rvalue_from_python_stage1_data py_s1_data;
    typedef boost::python::converter::rvalue_from_python_storage<nix::Value> py_storage;

    static PyObject* convert(const Value& value) {

        PyObject* module = PyImport_ImportModule("nixio.value");
        if (!module) return NULL;
        static PyObject* PyValueClass = PyObject_GetAttrString(module, "Value");

        DataType type = value.type();
        switch(type) {
            case DataType::Bool:
                return PyObject_CallFunction(PyValueClass, "O", value.get<bool>() ? Py_True: Py_False);
            case DataType::Float:
            case DataType::Double:
                return PyObject_CallFunction(PyValueClass, "d", value.get<double>());
            case DataType::Char:
            case DataType::Int8:
            case DataType::Int16:
            case DataType::Int32:
            case DataType::Int64:
                return PyObject_CallFunction(PyValueClass, "l", value.get<int64_t>());
            case DataType::UInt8:
            case DataType::UInt16:
            case DataType::UInt32:
            case DataType::UInt64:
                return PyObject_CallFunction(PyValueClass, "k", value.get<uint64_t>());
            case DataType::String:
                return PyObject_CallFunction(PyValueClass, "s", value.get<std::string>().c_str());
        }
    }

    // PyObject* -> nix::Value
    static void register_from_python() {
        boost::python::converter::registry::push_back(is_convertible,
                          construct, boost::python::type_id<Value>());
    }

    static void* is_convertible(PyObject* obj) {
        namespace bp = boost::python;

        // For now, simply check if it has a "value" attribute
        // TODO: Use PyObject_IsInstance

        if (PyObject_HasAttrString(obj, "value")) {
            return obj;
        } else {
            return nullptr;
        }
    }

    static void construct(PyObject* obj, py_s1_data* data) {
        namespace bp = boost::python;

        void* storage = ((py_storage*)data)->storage.bytes;


        PyObject* pyvalue = PyObject_GetAttrString(obj, "value");
        PyObject* pytype = PyObject_GetAttrString(obj, "data_type");
        std::string tname = extract<std::string>(PyObject_GetAttrString(pytype, "__name__"));

        if (tname == "uint8") {
            new (storage) Value(extract<uint8_t>(pyvalue));
        } else if (tname == "uint16") {
            new (storage) Value(extract<uint16_t>(pyvalue));
        } else if (tname == "uint32") {
            new (storage) Value(extract<uint32_t>(pyvalue));
        } else if (tname == "uint64") {
            new (storage) Value(extract<uint64_t>(pyvalue));
        } else if (tname == "int8") {
            new (storage) Value(extract<int8_t>(pyvalue));
        } else if (tname == "int16") {
            new (storage) Value(extract<int16_t>(pyvalue));
        } else if (tname == "int32") {
            new (storage) Value(extract<int32_t>(pyvalue));
        } else if (tname == "int64") {
            new (storage) Value(extract<int64_t>(pyvalue));
        } else if (tname == "bytes_" || tname == "string_") {
            new (storage) Value(extract<std::string>(pyvalue));
        } else if (tname == "bool_") {
            new (storage) Value(extract<bool>(pyvalue));
        } else if (tname == "float32") {
            new (storage) Value(extract<float>(pyvalue));
        } else if (tname == "float64") {
            new (storage) Value(extract<double>(pyvalue));
        } else {
            // TODO: Error
        }
        data->convertible = storage;
    }
};

void PyValue::do_export() {

    class_<Value>("Value")
        .def("__init__", make_constructor(create))
        .def_readwrite("reference", &Value::reference)
        .def_readwrite("filename", &Value::filename)
        .def_readwrite("encoder", &Value::encoder)
        .def_readwrite("checksum", &Value::checksum)
        .def_readwrite("uncertainty", &Value::uncertainty)
        .add_property("value", get, set)
        .add_property("data_type", &Value::type)
        // Other
        .def("__str__", &toStr<Value>)
        .def("__repr__", &toStr<Value>)
        ;

    to_python_converter<Value, value_transmogrify>();
    value_transmogrify::register_from_python();
    to_python_converter<std::vector<Value>, vector_transmogrify<Value>>();
    vector_transmogrify<Value>::register_from_python();
//    to_python_converter<boost::optional<Value>, option_transmogrify<Value>>();

}

}
