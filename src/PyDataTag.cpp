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

void setUnits(DataTag& dt, const std::vector<std::string>& units) {
    if (!units.empty())
        dt.units(units);
    else
        dt.units(boost::none);
}

// Extents

boost::optional<DataArray> getExtents(DataTag& dt) {
     DataArray da = dt.extents();
     if (da)
         return boost::optional<DataArray>(da);
     else
         return boost::none;
}

void setExtents(DataTag& dt, const boost::optional<DataArray>& data) {
    if (data)
        dt.extents(*data);
    else
        dt.extents(boost::none);
}

// getter for Reference

boost::optional<DataArray> getReferenceById(const DataTag& st, const std::string& id) {
    DataArray da = st.getReference(id);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

boost::optional<DataArray> getReferenceByPos(const DataTag& st, size_t index) {
    DataArray da = st.getReference(index);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

// operations for Feature

Feature createNewFeature(DataTag& dt, const DataArray &data, LinkType link_type) {
    Feature f = dt.createFeature(data, link_type);

    return f;
}

boost::optional<Feature> getFeatureById(const DataTag& st, const std::string& id) {
    Feature f = st.getFeature(id);

    return f ? boost::optional<Feature>(f) : boost::none;
}

boost::optional<Feature> getFeatureByPos(const DataTag& st, size_t index) {
    Feature f = st.getFeature(index);

    return f ? boost::optional<Feature>(f) : boost::none;
}

void PyDataTag::do_export() {

    PyEntityWithSources<base::IDataTag>::do_export("DataTag");

    class_<DataTag, bases<base::EntityWithSources<base::IDataTag>>>("DataTag")

        .add_property("positions",
                      GETTER(DataArray, DataTag, positions),
                      REF_SETTER(DataArray, DataTag, positions),
                      doc::data_tag_positions)
        .add_property("extents",
                      getExtents,
                      setExtents,
                      doc::data_tag_extents)
        .add_property("units",
                      GETTER(std::vector<std::string>, DataTag, units),
                      setUnits,
                      doc::data_tag_units)

        // References
        .def("_add_reference_by_id", REF_SETTER(std::string, DataTag, addReference))
        .def("_has_reference_by_id", CHECKER(std::string, DataTag, hasReference))
        .def("_reference_count", &DataTag::referenceCount)
        .def("_get_reference_by_id", &getReferenceById)
        .def("_get_reference_by_pos", &getReferenceByPos)
        .def("_delete_reference_by_id", REMOVER(std::string, DataTag, removeReference))

        // Features
        .def("create_feature", &createNewFeature, doc::data_tag_create_feature)
        .def("_has_feature_by_id", CHECKER(std::string, DataTag, hasFeature))
        .def("_feature_count", &DataTag::featureCount)
        .def("_get_feature_by_id", &getFeatureById)
        .def("_get_feature_by_pos", &getFeatureByPos)
        .def("_delete_feature_by_id", REMOVER(std::string, DataTag, deleteFeature))

        // Other
        .def("__str__", &toStr<DataTag>)
        .def("__repr__", &toStr<DataTag>)
        ;

    to_python_converter<std::vector<DataTag>, vector_transmogrify<DataTag>>();
    to_python_converter<boost::optional<DataTag>, option_transmogrify<DataTag>>();
}

}