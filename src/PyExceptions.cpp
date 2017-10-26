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

static void translateOutOfBounds(const nix::OutOfBounds &e) {
    PyErr_SetString(PyExc_IndexError, e.what());
}

static void translateDuplicateName(const nix::DuplicateName &e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
}

static void translateInvalidName(const nix::InvalidName &e) {
    PyErr_SetString(PyExc_NameError, e.what());
}

static void translateEmptyString(const nix::EmptyString &e) {
    PyErr_SetString(PyExc_NameError, e.what());
}

static void translateMissingAttr(const nix::MissingAttr &e) {
    PyErr_SetString(PyExc_AttributeError, e.what());
}

static void translateUninitializedEntity(const nix::UninitializedEntity &e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
}

static void translateUnsortedTicks(const nix::UnsortedTicks &e) {
    PyErr_SetString(PyExc_ValueError, e.what());
}

static void translateIncompatibleDimensions(const nix::IncompatibleDimensions &e) {
    PyErr_SetString(PyExc_ValueError, e.what());
}

static void translateInvalidDimension(const nix::InvalidDimension &e) {
    PyErr_SetString(PyExc_ValueError, e.what());
}

static void translateInvalidUnit(const nix::InvalidUnit &e) {
    PyErr_SetString(PyExc_ValueError, e.what());
}

static void translateInvalidRank(const nix::InvalidRank &e) {
    PyErr_SetString(PyExc_IndexError, e.what());
}

void PyException::do_export() {
    register_exception_translator<nix::OutOfBounds>(&translateOutOfBounds);
    register_exception_translator<nix::DuplicateName>(&translateDuplicateName);
    register_exception_translator<nix::InvalidName>(&translateInvalidName);
    register_exception_translator<nix::EmptyString>(&translateEmptyString);
    register_exception_translator<nix::InvalidRank>(&translateInvalidRank);
    register_exception_translator<nix::InvalidDimension>(&translateInvalidDimension);
    register_exception_translator<nix::InvalidUnit>(&translateInvalidUnit);
    register_exception_translator<nix::IncompatibleDimensions>(&translateIncompatibleDimensions);
    register_exception_translator<nix::UnsortedTicks>(&translateUnsortedTicks);
    register_exception_translator<nix::UninitializedEntity>(&translateUninitializedEntity);
    register_exception_translator<nix::MissingAttr>(&translateMissingAttr);
}

}
