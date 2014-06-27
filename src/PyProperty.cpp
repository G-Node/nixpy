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

void PyProperty::do_export() {

    PyNamedEntity<base::IProperty>::do_export("Property");
    class_<Property, bases<base::NamedEntity<base::IProperty>>>("Property")
        .def("__str__", &toStr<Property>)
        .def("__repr__", &toStr<Property>)
        ;
    to_python_converter<std::vector<Property>, vector_transmogrify<Property>>();
    to_python_converter<boost::optional<Property>, option_transmogrify<Property>>();
}

}
