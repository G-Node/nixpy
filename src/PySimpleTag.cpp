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

void setUnits(SimpleTag& st, const boost::optional<std::vector<std::string>> &units) {
    if (units)
        st.units(*units);
    else
        st.units(boost::none);
}

void setPosition(SimpleTag& st, const boost::optional<std::vector<double>> &pos) {
    if (pos)
        st.position(*pos);
    else
        st.position(boost::none);
}

void setExtent(SimpleTag& st, const boost::optional<std::vector<double>> &iextent) {
    if (iextent)
        st.extent(*iextent);
    else
        st.extent(boost::none);
}

// getter for Reference

boost::optional<DataArray> getReferenceById(const SimpleTag& st, const std::string& id) {
    DataArray da = st.getReference(id);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

boost::optional<DataArray> getReferenceByPos(const SimpleTag& st, size_t index) {
    DataArray da = st.getReference(index);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

// operations for Feature

Feature createNewFeature(SimpleTag& st, const DataArray &data, LinkType link_type) {
    Feature f = st.createFeature(data, link_type);

    return f;
}

boost::optional<Feature> getFeatureById(const SimpleTag& st, const std::string& id) {
    Feature f = st.getFeature(id);

    return f ? boost::optional<Feature>(f) : boost::none;
}

boost::optional<Feature> getFeatureByPos(const SimpleTag& st, size_t index) {
    Feature f = st.getFeature(index);

    return f ? boost::optional<Feature>(f) : boost::none;
}

void PySimpleTag::do_export() {

    PyEntityWithSources<base::ISimpleTag>::do_export("SimpleTag");

    class_<SimpleTag, bases<base::EntityWithSources<base::ISimpleTag>>>("SimpleTag")
        .add_property("units",
                      GETTER(std::vector<std::string>, SimpleTag, units),
                      setUnits)
        .add_property("position",
                      GETTER(std::vector<double>, SimpleTag, position),
                      setPosition)
        .add_property("extent",
                      GETTER(std::vector<double>, SimpleTag, extent),
                      setExtent)
        // References
        .def("add_reference", REF_SETTER(DataArray, SimpleTag, addReference))
        .def("_has_reference_by_id", CHECKER(std::string, SimpleTag, hasReference))
        .def("_reference_count", &SimpleTag::referenceCount)
        .def("_get_reference_by_id", &getReferenceById)
        .def("_get_reference_by_pos", &getReferenceByPos)
        .def("_delete_reference_by_id", REMOVER(std::string, SimpleTag, removeReference))
        // Features
        .def("create_feature", &createNewFeature)
        .def("_has_feature_by_id", CHECKER(std::string, SimpleTag, hasFeature))
        .def("_feature_count", &SimpleTag::featureCount)
        .def("_get_feature_by_id", &getFeatureById)
        .def("_get_feature_by_pos", &getFeatureByPos)
        .def("_delete_feature_by_id", REMOVER(std::string, SimpleTag, deleteFeature))
        // Other
        .def("__str__", &toStr<SimpleTag>)
        .def("__repr__", &toStr<SimpleTag>)
        ;

    to_python_converter<std::vector<SimpleTag>, vector_transmogrify<SimpleTag>>();
    to_python_converter<boost::optional<SimpleTag>, option_transmogrify<SimpleTag>>();
}

}