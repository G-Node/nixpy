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

static void translateInvalidName(const nix::InvalidName &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_NameError, "Invalid name given - names have to be sanitized using util function.");
    } else {
        PyErr_SetString(PyExc_NameError, e.what());
    }
}

static void translateEmptyString(const nix::EmptyString &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_NameError, "Empty string given - not a valid value for this field.");
    } else {
        PyErr_SetString(PyExc_NameError, e.what());
    }
}

static void translateMissingAttr(const nix::MissingAttr &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_AttributeError, "Obligatory attribute is not set!");
    } else {
        PyErr_SetString(PyExc_AttributeError, e.what());
    }
}

static void translateUninitializedEntity(const nix::UninitializedEntity &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_RuntimeError, "The Entity being accessed is uninitialized.");
    } else {
        PyErr_SetString(PyExc_RuntimeError, e.what());
    }
}

static void translateUnsortedTicks(const nix::UnsortedTicks &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_ValueError, "Ticks are not given in a ascending order.");
    } else {
        PyErr_SetString(PyExc_ValueError, e.what());
    }
}

static void translateIncompatibleDimensions(const nix::IncompatibleDimensions &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_ValueError, "The dimension descriptor is not compatible with the one stored int the dataArray!");
    } else {
        PyErr_SetString(PyExc_ValueError, e.what());
    }
}

static void translateInvalidDimension(const nix::InvalidDimension &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_ValueError, "The provided dimension descriptor is invalid in this context!");
    } else {
        PyErr_SetString(PyExc_ValueError, e.what());
    }
}

static void translateInvalidRank(const nix::InvalidRank &e) {
    if (emptyMessage(e.what())) {
        PyErr_SetString(PyExc_IndexError, "Invalid rank!");
    } else {
        PyErr_SetString(PyExc_IndexError, e.what());
    }
}

void PyException::do_export() {
    register_exception_translator<nix::OutOfBounds>(&translateOutOfBounds);
    register_exception_translator<nix::DuplicateName>(&translateDuplicateName);
    register_exception_translator<nix::InvalidName>(&translateInvalidName);
    register_exception_translator<nix::EmptyString>(&translateEmptyString);
    register_exception_translator<nix::InvalidRank>(&translateInvalidRank);
    register_exception_translator<nix::InvalidDimension>(&translateInvalidDimension);
    register_exception_translator<nix::IncompatibleDimensions>(&translateIncompatibleDimensions);
    register_exception_translator<nix::UnsortedTicks>(&translateUnsortedTicks);
    register_exception_translator<nix::UninitializedEntity>(&translateUninitializedEntity);
    register_exception_translator<nix::MissingAttr>(&translateMissingAttr);
}

}
