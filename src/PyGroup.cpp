// Copyright (c) 2015, German Neuroinformatics Node (G-Node)
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

// getter for DataArrays
boost::optional<DataArray> getDataArrayById(const Group& g, const std::string& id) {
    DataArray da = g.getDataArray(id);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

boost::optional<DataArray> getDataArrayByPos(const Group& g, size_t index) {
    DataArray da = g.getDataArray(index);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

// getter for Tags
boost::optional<Tag> getTagById(const Group& g, const std::string& id) {
    Tag t = g.getTag(id);

    return t? boost::optional<Tag>(t) : boost::none;
}

boost::optional<Tag> getTagByPos(const Group& g, size_t index) {
    Tag t = g.getTag(index);

    return t ? boost::optional<Tag>(t) : boost::none;
}

// getter for MultiTags
boost::optional<MultiTag> getMultiTagById(const Group& g, const std::string& id) {
    MultiTag t = g.getMultiTag(id);

    return t? boost::optional<MultiTag>(t) : boost::none;
}

boost::optional<MultiTag> getMultiTagByPos(const Group& g, size_t index) {
    MultiTag t = g.getMultiTag(index);

    return t ? boost::optional<MultiTag>(t) : boost::none;
}

void PyGroup::do_export() {

    PyEntityWithSources<base::IGroup>::do_export("Group");

    class_<Group, bases<base::EntityWithSources<base::IGroup>>>("Group")

        // DataArrays
        .def("_add_data_array_by_id", REF_SETTER(std::string, Group, addDataArray))
        .def("_has_data_array_by_id", CHECKER(std::string, Group, hasDataArray))
        .def("_data_array_count", &Group::dataArrayCount)
        .def("_get_data_array_by_id", &getDataArrayById)
        .def("_get_data_array_by_pos", &getDataArrayByPos)
        .def("_delete_data_array_by_id", REMOVER(std::string, Group, removeDataArray))
        // Tags
        .def("_add_tag_by_id", REF_SETTER(std::string, Group, addTag))
        .def("_has_tag_by_id", CHECKER(std::string, Group, hasTag))
        .def("_tag_count", &Group::tagCount)
        .def("_get_tag_by_id", &getTagById)
        .def("_get_tag_by_pos", &getTagByPos)
        .def("_delete_tag_by_id", REMOVER(std::string, Group, removeTag))
        // MultiTags
        .def("_add_multi_tag_by_id", REF_SETTER(std::string, Group, addMultiTag))
        .def("_has_multi_tag_by_id", CHECKER(std::string, Group, hasMultiTag))
        .def("_multi_tag_count", &Group::multiTagCount)
        .def("_get_multi_tag_by_id", &getMultiTagById)
        .def("_get_multi_tag_by_pos", &getMultiTagByPos)
        .def("_delete_multi_tag_by_id", REMOVER(std::string, Group, removeMultiTag))
        // Other
        .def("__str__", &toStr<Group>)
        .def("__repr__", &toStr<Group>)
        ;

    to_python_converter<std::vector<Group>, vector_transmogrify<Group>>();
    to_python_converter<boost::optional<Group>, option_transmogrify<Group>>();
}

}
