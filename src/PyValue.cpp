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
    } else if (PyInt_Check(value)) {
        int64_t conv = extract<int64_t>(value);
        created->set(conv);
    } else if (PyFloat_Check(value)) {
        double conv = extract<double>(value);
        created->set(conv);
    } else if (PyString_Check(value)) {
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
    } else if (PyInt_Check(value)) {
        int64_t conv = extract<int64_t>(value);
        ref.set(conv);
    } else if (PyFloat_Check(value)) {
        double conv = extract<double>(value);
        ref.set(conv);
    } else if (PyString_Check(value)) {
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
            return incref(object(ref.get<u_int64_t>()).ptr());
        case DataType::String:
            return incref(object(ref.get<std::string>()).ptr());
        case DataType::Date:
        case DataType::DateTime:
            // TODO support for date
            throw std::runtime_error("Wrong type");
        case DataType::Nothing:
        default:
            Py_RETURN_NONE;
    }
}

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

    to_python_converter<std::vector<Value>, vector_transmogrify<Value>>();
    vector_transmogrify<Value>::register_from_python();
    to_python_converter<boost::optional<Value>, option_transmogrify<Value>>();

}

}
