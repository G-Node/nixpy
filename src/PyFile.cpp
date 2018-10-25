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


//File open(std::string path, FileMode mode = FileMode::ReadWrite) {
//    return File::open(path, mode);
//}

File open(std::string path, std::string mode = "a") {
    FileMode nixmode;
    if (mode == "a") {
        nixmode = FileMode::ReadWrite;
    } else if (mode == "w") {
        nixmode = FileMode::Overwrite;
    } else if (mode == "r") {
        nixmode = FileMode::ReadOnly;
    } else {
      throw std::invalid_argument("File::open: invalid file mode flag (valid flags are: a, w, r for read-write, overwrite and read-only, respectively)!");
    }
    return File::open(path, nixmode);
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
        .add_property("version", &File::version, doc::file_version)
        .add_property("format", &File::format, doc::file_format)
        .add_property("created_at", &File::createdAt, doc::entity_crated_at)
        .def("force_created_at", &File::forceCreatedAt, doc::entity_force_created_at)
        .add_property("updated_at", &File::updatedAt, doc::entity_updated_at)
        .def("force_updated_at", &File::forceUpdatedAt, doc::entity_force_updated_at)
        // Block
        .def("create_block", &File::createBlock, doc::file_create_block)
        .def("_block_count", &File::blockCount)
        .def("_get_block_by_id", &getBlockById)
        .def("_get_block_by_pos", &getBlockByPos)
        .def("_delete_block_by_id", REMOVER(std::string, nix::File, deleteBlock))
        // Section
        .def("create_section", &File::createSection, doc::file_create_section)
        .def("_section_count", &File::sectionCount)
        .def("_get_section_by_id", &getSectionById)
        .def("_get_section_by_pos", &getSectionByPos)
        .def("_delete_section_by_id", REMOVER(std::string, nix::File, deleteSection))
        // Open and close
        .def("is_open", &File::isOpen, doc::file_is_open)
        .def("close", &File::close, doc::file_close)
        .def("flush", &File::flush)
        .def("open", open, open_overloads())
        .staticmethod("open")
        // Other
        .def("validate", &File::validate)
        .def(self == other<File>())
        ;

        to_python_converter<boost::optional<File>, option_transmogrify<File>>();

}

}
