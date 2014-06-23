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


File open(std::string path, FileMode mode = FileMode::ReadWrite) {
    return File::open(path, mode);
}

BOOST_PYTHON_FUNCTION_OVERLOADS(open_overloads, open, 1, 2)

// getter for Block

boost::optional<Block> getBlockById(const File& file, const std::string& id) {
    Block bl = file.getBlock(id);

    return bl ? boost::optional<Block>(bl) : boost::none;
}

boost::optional<Block> getBlockByPos(const File& file, size_t index) {
    Block bl = file.getBlock(index);

    return bl ? boost::optional<Block>(bl) : boost::none;
}

std::vector<Block> file_blocks ( const File &f ) {
    return f.blocks();
}

// getter for Section

boost::optional<Section> getSectionById(const File& file, const std::string& id) {
    Section sec = file.getSection(id);

    return sec ? boost::optional<Section>(sec) : boost::none;
}

boost::optional<Section> getSectionByPos(const File& file, size_t index) {
    Section sec = file.getSection(index);

    return sec ? boost::optional<Section>(sec) : boost::none;
}

void PyFile::do_export() {

    enum_<FileMode>("FileMode")
        .value("ReadOnly",  FileMode::ReadOnly)
        .value("ReadWrite", FileMode::ReadWrite)
        .value("Overwrite", FileMode::Overwrite)
        ;

    class_<File>("File")
        .add_property("version", &File::version)
        .add_property("format", &File::format)
        .add_property("created_at", &File::createdAt)
        .def("force_created_at", &File::forceCreatedAt)
        .add_property("updated_at", &File::updatedAt)
        .def("force_updated_at", &File::forceUpdatedAt)
        // Block
        .def("create_block", &File::createBlock)
        .def("_block_count", &File::blockCount)
        .def("_get_block_by_id", &getBlockById)
        .def("_get_block_by_pos", &getBlockByPos)
        .def("_delete_block_by_id", REMOVER(std::string, nix::File, deleteBlock))
        // Section
        .def("create_section", &File::createSection)
        .def("_section_count", &File::sectionCount)
        .def("_get_section_by_id", &getSectionById)
        .def("_get_section_by_pos", &getSectionByPos)
        .def("_delete_section_by_id", REMOVER(std::string, nix::File, deleteSection))
        // Open and close
        .def("is_open", &File::isOpen)
        .def("close", &File::close)
        .def("open", open, open_overloads())
        .staticmethod("open")
        // Other
        .def(self == other<File>())
        ;

        to_python_converter<boost::optional<File>, option_transmogrify<File>>();

}

}
