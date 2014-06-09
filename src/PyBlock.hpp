// Copyright (c) 2013, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE file in the root of the Project.

#ifndef NIXPY_BLOCK_H
#define NIXPY_BLOCK_H

#include <boost/python.hpp>
#include <boost/optional.hpp>

#include <nix.hpp>
#include <accessors.hpp>
#include <PyEntity.hpp>

namespace nixpy {

struct PyBlock {

    static std::vector<nix::DataArray> nix_block_data_arrays (const nix::Block &b) {
        return b.dataArrays();
    }

    static void do_export() {
        using namespace boost::python;

        PyEntityWithMetadata<nix::base::IBlock>::do_export("IBlock");
        class_<nix::Block, bases<nix::base::EntityWithMetadata<nix::base::IBlock>>>("Block")
            .def("create_data_array", &nix::Block::createDataArray)
            .def("data_array_count", &nix::Block::dataArrayCount)
            .def("data_arrays", nix_block_data_arrays)
            .def(self == self)
            ;

        to_python_converter<std::vector<nix::Block>, vector_transmogrify<nix::Block>>();
        to_python_converter<boost::optional<nix::Block>, option_transmogrify<nix::Block>>();

    }

};

}

#endif
