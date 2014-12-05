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
#include <nix/valid/result.hpp>
#include <accessors.hpp>
#include <transmorgify.hpp>
#include <docstrings.hpp>

#include <PyEntity.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

void PyResult::do_export() {

    class_<valid::Message>("Message",
                           init<std::string, std::string>())
        .def_readonly("id", &valid::Message::id)
        .def_readonly("msg", &valid::Message::msg);

    class_<valid::Result>("Result",
                          init<std::vector<valid::Message>, std::vector<valid::Message>>())
        .add_property("errors", &valid::Result::getErrors)
        .add_property("warnings", &valid::Result::getWarnings)
        .def("is_ok", &valid::Result::ok)
        .def("has_errors", &valid::Result::hasErrors)
        .def("has_warnings", &valid::Result::hasWarnings);

    to_python_converter<std::vector<valid::Message>, vector_transmogrify<valid::Message>>();
    vector_transmogrify<valid::Message>::register_from_python();

    to_python_converter<std::vector<valid::Result>, vector_transmogrify<valid::Result>>();
    vector_transmogrify<valid::Result>::register_from_python();

}

}
