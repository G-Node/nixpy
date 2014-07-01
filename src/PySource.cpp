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


void PySource::do_export() {

    PyEntityWithMetadata<base::ISource>::do_export("Source");

    class_<Source, bases<base::EntityWithMetadata<base::ISource>>>("Source")
        .def("__str__", &toStr<Source>)
        .def("__repr__", &toStr<Source>)
        .def(self == self)
        ;

    to_python_converter<std::vector<Source>, vector_transmogrify<Source>>();
    to_python_converter<boost::optional<Source>, option_transmogrify<Source>>();
}

}
