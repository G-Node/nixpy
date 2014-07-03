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

void PyFeature::do_export() {

    PyEntity<base::IFeature>::do_export("Feature");

    class_<Feature, bases<base::Entity<base::IFeature>>>("Feature")
        .add_property("link_type",
                      GETTER(LinkType, Feature, linkType),
                      SETTER(LinkType, Feature, linkType))
        ;

    to_python_converter<std::vector<Feature>, vector_transmogrify<Feature>>();
    to_python_converter<boost::optional<Feature>, option_transmogrify<Feature>>();
}

}