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
#include <docstrings.hpp>

#include <PyEntity.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

// Definition

void setDefinition(Property& prop, const boost::optional<std::string>& str) {
    if (str)
        prop.definition(*str);
    else
        prop.definition(boost::none);
}

// Mapping

void setMapping(Property& prop, const boost::optional<std::string>& str) {
    if (str)
        prop.mapping(*str);
    else
        prop.mapping(boost::none);
}

// Unit

void setUnit(Property& prop, const boost::optional<std::string>& str) {
    if (str)
        prop.unit(*str);
    else
        prop.unit(boost::none);
}

// Values
struct value_transmogrify {
    typedef boost::python::converter::rvalue_from_python_stage1_data py_s1_data;
    typedef boost::python::converter::rvalue_from_python_storage<nix::Value> py_storage;

    // nix::Value -> PyObject*
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

    // PyObject* -> nix::Value
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

void PyProperty::do_export() {

    PyEntity<base::IProperty>::do_export("Property");
    class_<Property, bases<base::Entity<base::IProperty>>>("Property")
        .add_property("name",
                      GETTER(std::string, Property, name),
                      doc::entity_name)
        .add_property("definition",
                      OPT_GETTER(std::string, Property, definition),
                      setDefinition,
                      doc::entity_definition)
        .add_property("mapping",
                      OPT_GETTER(std::string, Property, mapping),
                      setMapping)
        .add_property("unit",
                      OPT_GETTER(std::string, Property, unit),
                      setUnit)
        .add_property("data_type", &Property::dataType)
        .add_property("values",
                      GETTER(std::vector<Value>, Property, values),
                      REF_SETTER(std::vector<Value>, Property, values))
        .def("delete_values", &Property::deleteValues)
        .def("__str__", &toStr<Property>)
        .def("__repr__", &toStr<Property>)
        ;

    to_python_converter<std::vector<Property>, vector_transmogrify<Property>>();
    to_python_converter<boost::optional<Property>, option_transmogrify<Property>>();

    to_python_converter<Value, value_transmogrify>();
    value_transmogrify::register_from_python();
    to_python_converter<std::vector<Value>, vector_transmogrify<Value>>();
    vector_transmogrify<Value>::register_from_python();
}

}
