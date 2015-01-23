// Copyright (c) 2014, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE source in the root of the Project.

#include <boost/python.hpp>
#include <boost/optional.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/exception_translator.hpp>

#include <nix.hpp>

#include <accessors.hpp>
#include <transmorgify.hpp>

#include <PyEntity.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

static bool emptyMessage(const char* message) {
    return std::strlen(message) == 0;
}

static void translateOutOfBounds(const nix::OutOfBounds &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_IndexError, "Attempt to access data with an index that is out of bounds!");
    } else {
        PyErr_SetString(PyExc_IndexError, e.what());
    }
}

static void translateDuplicateName(const nix::DuplicateName &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_RuntimeError, "Duplicate name given - names have to be unique for a given entity type & parent.");
    } else {
        PyErr_SetString(PyExc_RuntimeError, e.what());
    }
}

void PyException::do_export() {
    register_exception_translator<nix::OutOfBounds>(&translateOutOfBounds);
    register_exception_translator<nix::DuplicateName>(&translateDuplicateName);
}

}
