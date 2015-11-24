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
        // Features
        /*
        .def("create_feature", &createNewFeature, doc::tag_create_feature)
        .def("_has_feature_by_id", CHECKER(std::string, Tag, hasFeature))
        .def("_feature_count", &Tag::featureCount)
        .def("_get_feature_by_id", &getFeatureById)
        .def("_get_feature_by_pos", &getFeatureByPos)
        .def("_delete_feature_by_id", REMOVER(std::string, Tag, deleteFeature))
        // Data access
        .def("retrieve_data", &Tag::retrieveData)
        .def("retrieve_feature_data", &Tag::retrieveFeatureData)
        */
        // Other
        .def("__str__", &toStr<Tag>)
        .def("__repr__", &toStr<Tag>)
        ;

    to_python_converter<std::vector<Tag>, vector_transmogrify<Tag>>();
    to_python_converter<boost::optional<Tag>, option_transmogrify<Tag>>();
}

}
