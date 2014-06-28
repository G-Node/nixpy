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
#include <PyValue.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

void PyValue::do_export() {

    class_<Value>("Value")
        .def_readwrite("reference", &Value::reference)
        .def_readwrite("filename", &Value::filename)
        .def_readwrite("encoder", &Value::encoder)
        .def_readwrite("checksum", &Value::checksum)
        ;

    to_python_converter<std::vector<Value>, vector_transmogrify<Value>>();
    vector_transmogrify<Value>::register_from_python();
    to_python_converter<boost::optional<Value>, option_transmogrify<Value>>();

}

}
