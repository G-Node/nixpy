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

void setUnits(Tag& st, const std::vector<std::string>& units) {
    if (!units.empty())
        st.units(units);
    else
        st.units(boost::none);
}


void setExtent(Tag& st, const std::vector<double>& iextent) {
    if (!iextent.empty())
        st.extent(iextent);
    else
        st.extent(boost::none);
}

// getter for Reference

boost::optional<DataArray> getReferenceById(const Tag& st, const std::string& id) {
    DataArray da = st.getReference(id);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

boost::optional<DataArray> getReferenceByPos(const Tag& st, size_t index) {
    DataArray da = st.getReference(index);

    return da ? boost::optional<DataArray>(da) : boost::none;
}

// operations for Feature

Feature createNewFeature(Tag& st, const DataArray &data, const std::string& link_type) {

    LinkType lt;
    if (link_type == "Tagged")
        lt = LinkType::Tagged;
    else if (link_type == "Untagged")
        lt = LinkType::Untagged;
    else if (link_type == "Indexed")
        lt = LinkType::Indexed;
    // TODO: Throw error

    return st.createFeature(data, lt);
}

boost::optional<Feature> getFeatureById(const Tag& st, const std::string& id) {
    Feature f = st.getFeature(id);

    return f ? boost::optional<Feature>(f) : boost::none;
}

boost::optional<Feature> getFeatureByPos(const Tag& st, size_t index) {
    Feature f = st.getFeature(index);

    return f ? boost::optional<Feature>(f) : boost::none;
}

void PyTag::do_export() {

    PyEntityWithSources<base::ITag>::do_export("Tag");

    class_<Tag, bases<base::EntityWithSources<base::ITag>>>("Tag")

        // TODO make tuples for simple vectors like units, position, extent

        .add_property("units",
                      GETTER(std::vector<std::string>, Tag, units),
                      setUnits,
                      doc::tag_units)
        .add_property("position",
                      GETTER(std::vector<double>, Tag, position),
                      SETTER(std::vector<double> &, Tag, position),
                      doc::tag_position)
        .add_property("extent",
                      GETTER(std::vector<double>, Tag, extent),
                      setExtent,
                      doc::tag_extent)
        // References
        .def("_add_reference_by_id", REF_SETTER(std::string, Tag, addReference))
        .def("_has_reference_by_id", CHECKER(std::string, Tag, hasReference))
        .def("_reference_count", &Tag::referenceCount)
        .def("_get_reference_by_id", &getReferenceById)
        .def("_get_reference_by_pos", &getReferenceByPos)
        .def("_delete_reference_by_id", REMOVER(std::string, Tag, removeReference))
        // Features
        .def("create_feature", &createNewFeature, doc::tag_create_feature)
        .def("_has_feature_by_id", CHECKER(std::string, Tag, hasFeature))
        .def("_feature_count", &Tag::featureCount)
        .def("_get_feature_by_id", &getFeatureById)
        .def("_get_feature_by_pos", &getFeatureByPos)
        .def("_delete_feature_by_id", REMOVER(std::string, Tag, deleteFeature))
        // Data access
        .def("retrieve_data", &Tag::retrieveData)
        .def("retrieve_feature_data", &Tag::retrieveFeatureData)
        // Other
        .def("__str__", &toStr<Tag>)
        .def("__repr__", &toStr<Tag>)
        ;

    to_python_converter<std::vector<Tag>, vector_transmogrify<Tag>>();
    to_python_converter<boost::optional<Tag>, option_transmogrify<Tag>>();
}

}
