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
#include <PyBlock.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

std::vector<DataArray> nix_block_data_arrays (const Block &b) {
    return b.dataArrays();
}

// getter for DataArray

boost::optional<DataArray> getDataArrayById(const Block& block, const std::string& id) {
    DataArray da = block.getDataArray(id);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

boost::optional<DataArray> getDataArrayByPos(const Block& block, size_t index) {
    DataArray da = block.getDataArray(index);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

// getter for DataTag

boost::optional<DataTag> getDataTagById(const Block& block, const std::string& id) {
    DataTag da = block.getDataTag(id);

    return da ? boost::optional<DataTag>(da) : boost::none;
}

boost::optional<DataTag> getDataTagByPos(const Block& block, size_t index) {
    DataTag da = block.getDataTag(index);

    return da ? boost::optional<DataTag>(da) : boost::none;
}

// getter for SimpleTag

boost::optional<SimpleTag> getSimpleTagById(const Block& block, const std::string& id) {
    SimpleTag da = block.getSimpleTag(id);

    return da ? boost::optional<SimpleTag>(da) : boost::none;
}

boost::optional<SimpleTag> getSimpleTagByPos(const Block& block, size_t index) {
    SimpleTag da = block.getSimpleTag(index);

    return da ? boost::optional<SimpleTag>(da) : boost::none;
}

// getter for Source

boost::optional<Source> getSourceById(const Block& block, const std::string& id) {
    Source da = block.getSource(id);

    return da ? boost::optional<Source>(da) : boost::none;
}

boost::optional<Source> getSourceByPos(const Block& block, size_t index) {
    Source da = block.getSource(index);

    return da ? boost::optional<Source>(da) : boost::none;
}

void PyBlock::do_export() {
    PyEntityWithMetadata<base::IBlock>::do_export("Block");

    class_<Block, bases<base::EntityWithMetadata<base::IBlock>>>("Block")
        // DataArray
        .def("create_data_array", &Block::createDataArray)
        .def("_data_array_count", &Block::dataArrayCount)
        .def("_get_data_array_by_id", &getDataArrayById)
        .def("_get_data_array_by_pos", &getDataArrayByPos)
        .def("_delete_data_array_by_id", REMOVER(std::string, nix::Block, deleteDataArray))
        // DataTag
        .def("create_data_tag", &Block::createDataTag)
        .def("_data_tag_count", &Block::dataTagCount)
        .def("_get_data_tag_by_id", &getDataTagById)
        .def("_get_data_tag_by_pos", &getDataTagByPos)
        .def("_delete_data_tag_by_id", REMOVER(std::string, nix::Block, deleteDataTag))
        // SimpleTag
        .def("create_simple_tag", &Block::createSimpleTag)
        .def("_simple_tag_count", &Block::simpleTagCount)
        .def("_get_simple_tag_by_id", &getSimpleTagById)
        .def("_get_simple_tag_by_pos", &getSimpleTagByPos)
        .def("_delete_simple_tag_by_id", REMOVER(std::string, nix::Block, deleteSimpleTag))
        // Source
        .def("create_source", &Block::createSource)
        .def("_source_count", &Block::sourceCount)
        .def("_get_source_by_id", &getSourceById)
        .def("_get_source_by_pos", &getSourceByPos)
        .def("_delete_source_by_id", REMOVER(std::string, nix::Block, deleteSource))
        .def("__str__", &toStr<Block>)
        .def("__repr__", &toStr<Block>)
        .def(self == self)
        ;

    to_python_converter<std::vector<Block>, vector_transmogrify<Block>>();
    to_python_converter<boost::optional<Block>, option_transmogrify<Block>>();
}

}
