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
PyObject* get_PyValueObj() {
    PyObject* module = PyImport_ImportModule("nixio.value");
    if (!module) return NULL;
    return PyObject_GetAttrString(module, "Value");
}

Value toNixValue(PyObject* obj) {
    PyObject* pyvalue = PyObject_GetAttrString(obj, "value");
    PyObject* pytype = PyObject_GetAttrString(obj, "data_type");
    std::string tname = extract<std::string>(PyObject_GetAttrString(pytype, "__name__"));

    if (tname == "uint8") {
        return Value(extract<uint8_t>(pyvalue));
    } else if (tname == "uint16") {
        return Value(extract<uint16_t>(pyvalue));
    } else if (tname == "uint32") {
        return Value(extract<uint32_t>(pyvalue));
    } else if (tname == "uint64") {
        return Value(extract<uint64_t>(pyvalue));
    } else if (tname == "int8") {
        return Value(extract<int8_t>(pyvalue));
    } else if (tname == "int16") {
        return Value(extract<int16_t>(pyvalue));
    } else if (tname == "int32") {
        return Value(extract<int32_t>(pyvalue));
    } else if (tname == "int64") {
        return Value(extract<uint64_t>(pyvalue));
    } else if (tname == "bytes_" || tname == "string_") {
        return Value(extract<std::string>(pyvalue));
    } else if (tname == "bool_") {
        return Value(extract<bool>(pyvalue));
    } else if (tname == "float32") {
        return Value(extract<float>(pyvalue));
    } else if (tname == "float64") {
        return Value(extract<double>(pyvalue));
    } else {
        // TODO: Error
    }
}

void setValues(Property& prop, list& pyvaluelist) {
    std::vector<Value> nixvaluelist;
    for (int idx = 0; idx < len(pyvaluelist); ++idx) {
        nixvaluelist.push_back(toNixValue(object(pyvaluelist[idx]).ptr()));
    }
    prop.values(nixvaluelist);
}

PyObject* toPyValue(const Value& value) {
    static PyObject* PyValue = get_PyValueObj();
    DataType type = value.type();
    switch(type) {
        case DataType::Bool:
            return PyObject_CallFunction(PyValue, "O", value.get<bool>() ? Py_True: Py_False);
        case DataType::Float:
        case DataType::Double:
            return PyObject_CallFunction(PyValue, "d", value.get<double>());
        case DataType::Char:
        case DataType::Int8:
        case DataType::Int16:
        case DataType::Int32:
        case DataType::Int64:
            return PyObject_CallFunction(PyValue, "l", value.get<int64_t>());
        case DataType::UInt8:
        case DataType::UInt16:
        case DataType::UInt32:
        case DataType::UInt64:
            return PyObject_CallFunction(PyValue, "k", value.get<uint64_t>());
        case DataType::String:
            return PyObject_CallFunction(PyValue, "s", value.get<std::string>().c_str());
    }
}

PyObject* getValues(Property& prop) {
    PyObject* valuelist = PyList_New(0);
    std::vector<Value> nixvaluelist = prop.values();
    for (Value item : nixvaluelist) {
        PyList_Append(valuelist, toPyValue(item));
    }
    return valuelist;
}

void PyProperty::do_export() {

    enum_<DataType>("CDataType")
        .value("Bool"    , DataType::Bool)
        .value("Char"    , DataType::Char)
        .value("Float"   , DataType::Float)
        .value("Double"  , DataType::Double)
        .value("Int8"    , DataType::Int8)
        .value("Int16"   , DataType::Int16)
        .value("Int32"   , DataType::Int32)
        .value("Int64"   , DataType::Int64)
        .value("UInt8"   , DataType::UInt8)
        .value("UInt16"  , DataType::UInt16)
        .value("UInt32"  , DataType::UInt32)
        .value("UInt64"  , DataType::UInt64)
        .value("String"  , DataType::String)
        .value("Nothing" , DataType::Nothing)
        ;

    to_python_converter<boost::optional<DataType>, option_transmogrify<DataType>>();
    option_transmogrify<DataType>::register_from_python();

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
                      getValues,
                      setValues)
//                      GETTER(std::vector<Value>, Property, values),
//                      REF_SETTER(std::vector<Value>, Property, values))
        .def("delete_values", &Property::deleteValues)
        .def("__str__", &toStr<Property>)
        .def("__repr__", &toStr<Property>)
        ;

    to_python_converter<std::vector<Property>, vector_transmogrify<Property>>();
    to_python_converter<boost::optional<Property>, option_transmogrify<Property>>();
}

}
