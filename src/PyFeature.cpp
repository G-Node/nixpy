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

void setLinkType(Feature& f, const std::string& link_type) {
    LinkType lt;
    if (link_type == "Tagged")
        lt = LinkType::Tagged;
    else if (link_type == "Untagged")
        lt = LinkType::Untagged;
    else if (link_type == "Indexed")
        lt = LinkType::Indexed;
    else throw std::runtime_error("Invalid string for LinkType.");

    f.linkType(lt);
}

static std::string getLinkType(Feature& f) {
    return link_type_to_string(f.linkType());
}

void PyFeature::do_export() {

    PyEntity<base::IFeature>::do_export("Feature");

    class_<Feature, bases<base::Entity<base::IFeature>>>("Feature")
        .add_property("link_type",
                      getLinkType,
                      setLinkType)
        .add_property("data",
                      GETTER(DataArray, Feature, data),
                      REF_SETTER(DataArray, Feature, data))
        ;

    to_python_converter<std::vector<Feature>, vector_transmogrify<Feature>>();
    to_python_converter<boost::optional<Feature>, option_transmogrify<Feature>>();
}

}