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

Feature createNewFeature(MultiTag& dt, const DataArray &data, LinkType link_type) {
    Feature f = dt.createFeature(data, link_type);

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

        // Data
        .def("retrieve_data", &MultiTag::retrieveData)

        // Other
        .def("__str__", &toStr<MultiTag>)
        .def("__repr__", &toStr<MultiTag>)
        ;

    to_python_converter<std::vector<MultiTag>, vector_transmogrify<MultiTag>>();
    to_python_converter<boost::optional<MultiTag>, option_transmogrify<MultiTag>>();
}

}
