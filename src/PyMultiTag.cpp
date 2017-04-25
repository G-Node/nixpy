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

// Units

void setUnits(MultiTag& dt, const std::vector<std::string>& units) {
    if (!units.empty())
        dt.units(units);
    else
        dt.units(boost::none);
}

// Extents

boost::optional<DataArray> getExtents(MultiTag& dt) {
     DataArray da = dt.extents();
     if (da)
         return boost::optional<DataArray>(da);
     else
         return boost::none;
}

void setExtents(MultiTag& dt, const boost::optional<DataArray>& data) {
    if (data)
        dt.extents(*data);
    else
        dt.extents(boost::none);
}

// getter for Reference

boost::optional<DataArray> getReferenceById(const MultiTag& st, const std::string& id) {
    DataArray da = st.getReference(id);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

boost::optional<DataArray> getReferenceByPos(const MultiTag& st, size_t index) {
    DataArray da = st.getReference(index);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

// operations for Feature

Feature createNewFeature(MultiTag& dt, const DataArray &data, const std::string& link_type) {
    LinkType lt;
    if (link_type == "Tagged")
        lt = LinkType::Tagged;
    else if (link_type == "Untagged")
        lt = LinkType::Untagged;
    else if (link_type == "Indexed")
        lt = LinkType::Indexed;
    // TODO: Throw error

    Feature f = dt.createFeature(data, lt);

    return f;
}

boost::optional<Feature> getFeatureById(const MultiTag& st, const std::string& id) {
    Feature f = st.getFeature(id);

    return f ? boost::optional<Feature>(f) : boost::none;
}

boost::optional<Feature> getFeatureByPos(const MultiTag& st, size_t index) {
    Feature f = st.getFeature(index);

    return f ? boost::optional<Feature>(f) : boost::none;
}

DataView retrieveDataIdx(const MultiTag& st, size_t position_index, size_t reference_index) {
    return st.retrieveData(position_index, reference_index);
}

DataView retrieveDataStr(const MultiTag& st, size_t position_index, const std::string &name_or_id) {
    return st.retrieveData(position_index, name_or_id);
}

DataView retrieveFeatureDataIdx(const MultiTag& st, size_t position_index, size_t feature_index) {
    return st.retrieveFeatureData(position_index, feature_index);
}

DataView retrieveFeatureDataStr(const MultiTag& st, size_t position_index, const std::string &name_or_id) {
    return st.retrieveFeatureData(position_index, name_or_id);
}

void PyMultiTag::do_export() {

    PyEntityWithSources<base::IMultiTag>::do_export("MultiTag");

    class_<MultiTag, bases<base::EntityWithSources<base::IMultiTag>>>("MultiTag")

        .add_property("positions",
                      GETTER(DataArray, MultiTag, positions),
                      REF_SETTER(DataArray, MultiTag, positions),
                      doc::multi_tag_positions)
        .add_property("extents",
                      getExtents,
                      setExtents,
                      doc::multi_tag_extents)
        .add_property("units",
                      GETTER(std::vector<std::string>, MultiTag, units),
                      setUnits,
                      doc::multi_tag_units)

        // References
        .def("_add_reference_by_id", REF_SETTER(std::string, MultiTag, addReference))
        .def("_has_reference_by_id", CHECKER(std::string, MultiTag, hasReference))
        .def("_reference_count", &MultiTag::referenceCount)
        .def("_get_reference_by_id", &getReferenceById)
        .def("_get_reference_by_pos", &getReferenceByPos)
        .def("_delete_reference_by_id", REMOVER(std::string, MultiTag, removeReference))

        // Features
        .def("create_feature", &createNewFeature, doc::multi_tag_create_feature)
        .def("_has_feature_by_id", CHECKER(std::string, MultiTag, hasFeature))
        .def("_feature_count", &MultiTag::featureCount)
        .def("_get_feature_by_id", &getFeatureById)
        .def("_get_feature_by_pos", &getFeatureByPos)
        .def("_delete_feature_by_id", REMOVER(std::string, MultiTag, deleteFeature))

        // Data access
        .def("retrieve_data", &retrieveDataIdx)
        .def("retrieve_data", &retrieveDataStr)
        .def("retrieve_feature_data", &retrieveFeatureDataIdx)
        .def("retrieve_feature_data", &retrieveFeatureDataStr)

        // Other
        .def("__str__", &toStr<MultiTag>)
        .def("__repr__", &toStr<MultiTag>)
        ;

    to_python_converter<std::vector<MultiTag>, vector_transmogrify<MultiTag>>();
    to_python_converter<boost::optional<MultiTag>, option_transmogrify<MultiTag>>();
}

}
