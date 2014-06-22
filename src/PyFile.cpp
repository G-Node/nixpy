// Copyright (c) 2013, German Neuroinformatics Node (G-Node)
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
#include <PyFile.hpp>


using namespace nix;
using namespace boost::python;

namespace nixpy {


File file_open ( std::string path ) {
    return File::open ( path );
}

std::vector<Block> file_blocks ( const File &f ) {
    return f.blocks();
}

void PyFile::do_export() {

    class_<File>("File")
        .add_property("version", &File::version)
        .def("open", file_open)
        .def("blocks", file_blocks)
        .def("create_block", &File::createBlock)
        .def(self == other<File>())
        .staticmethod("open")
        ;

}

}
