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

DataArray createDataArray(Block& block, const std::string &name, const std::string &type,
                          DataType data_type, const NDSize &shape,
                          const std::string &compression) {
    return block.createDataArray(name, type, data_type, shape, pyCompressionToNix(compression));
}

// getter for MultiTag

boost::optional<MultiTag> getMultiTagById(const Block& block, const std::string& id) {
    MultiTag da = block.getMultiTag(id);

    return da ? boost::optional<MultiTag>(da) : boost::none;
}

boost::optional<MultiTag> getMultiTagByPos(const Block& block, size_t index) {
    MultiTag da = block.getMultiTag(index);

    return da ? boost::optional<MultiTag>(da) : boost::none;
}

// getter for Tag

boost::optional<Tag> getTagById(const Block& block, const std::string& id) {
    Tag da = block.getTag(id);

    return da ? boost::optional<Tag>(da) : boost::none;
}

boost::optional<Tag> getTagByPos(const Block& block, size_t index) {
    Tag da = block.getTag(index);

    return da ? boost::optional<Tag>(da) : boost::none;
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

// getter for Group

boost::optional<Group> getGroupById(const Block& block, const std::string& id) {
    Group g = block.getGroup(id);

    return g ? boost::optional<Group>(g) : boost::none;
}

boost::optional<Group> getGroupByPos(const Block& block, size_t index) {
    Group g = block.getGroup(index);

    return g ? boost::optional<Group>(g) : boost::none;
}

void PyBlock::do_export() {
    PyEntityWithMetadata<base::IBlock>::do_export("Block");

    class_<Block, bases<base::EntityWithMetadata<base::IBlock>>>("Block")
        // DataArray
        .def("_create_data_array", createDataArray)
        .def("_data_array_count", &Block::dataArrayCount)
        .def("_get_data_array_by_id", &getDataArrayById)
        .def("_get_data_array_by_pos", &getDataArrayByPos)
        .def("_delete_data_array_by_id", REMOVER(std::string, nix::Block, deleteDataArray))
        // MultiTag
        .def("create_multi_tag", &Block::createMultiTag, doc::block_create_multi_tag)
        .def("_multi_tag_count", &Block::multiTagCount)
        .def("_get_multi_tag_by_id", &getMultiTagById)
        .def("_get_multi_tag_by_pos", &getMultiTagByPos)
        .def("_delete_multi_tag_by_id", REMOVER(std::string, nix::Block, deleteMultiTag))
        // Tag
        .def("create_tag", &Block::createTag, doc::block_create_tag)
        .def("_tag_count", &Block::tagCount)
        .def("_get_tag_by_id", &getTagById)
        .def("_get_tag_by_pos", &getTagByPos)
        .def("_delete_tag_by_id", REMOVER(std::string, nix::Block, deleteTag))
        // Source
        .def("create_source", &Block::createSource, doc::block_create_source)
        .def("_source_count", &Block::sourceCount)
        .def("_get_source_by_id", &getSourceById)
        .def("_get_source_by_pos", &getSourceByPos)
        .def("_delete_source_by_id", REMOVER(std::string, nix::Block, deleteSource))
        // Group
        .def("create_group", &Block::createGroup, doc::block_create_group)
        .def("_group_count", &Block::groupCount)
        .def("_get_group_by_id", &getGroupById)
        .def("_get_group_by_pos", &getGroupByPos)
        .def("_delete_group_by_id", REMOVER(std::string, nix::Block, deleteGroup))
        // Other
        .def("__str__", &toStr<Block>)
        .def("__repr__", &toStr<Block>)
        ;

    to_python_converter<std::vector<Block>, vector_transmogrify<Block>>();
    to_python_converter<boost::optional<Block>, option_transmogrify<Block>>();
}

}
