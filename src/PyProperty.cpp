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
#include <PyProperty.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

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

void PyProperty::do_export() {

    enum_<DataType>("DataType")
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
        .value("Date"    , DataType::Date)
        .value("DateTime", DataType::DateTime)
        .value("Nothing" , DataType::Nothing)
        ;

    to_python_converter<boost::optional<DataType>, option_transmogrify<DataType>>();
    option_transmogrify<DataType>::register_from_python();

    PyNamedEntity<base::IProperty>::do_export("Property");
    class_<Property, bases<base::NamedEntity<base::IProperty>>>("Property")
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
        .def("__str__", &toStr<Property>)
        .def("__repr__", &toStr<Property>)
        ;

    to_python_converter<std::vector<Property>, vector_transmogrify<Property>>();
    to_python_converter<boost::optional<Property>, option_transmogrify<Property>>();
}

}
