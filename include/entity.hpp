// Copyright (c) 2013, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE file in the root of the Project.

#ifndef NIXPY_ENTITY_H
#define NIXPY_ENTITY_H

#include <boost/python.hpp>

#include <nix.hpp>

namespace nixpy {

/**
 * Exports a specialisation of nix::base::Entity wich can be further used
 * as a subclass.
 *
 * @param name          A unique name of the specialisation.
 *                      Converntion: just the class name.
 */
template<typename T>
void export_entity(const std::string& name) {
    using namespace boost::python;

    std::string real_name = "__Entity" + name;
    class_<nix::base::Entity<T>>(real_name.c_str(), no_init)
        .add_property("id", &nix::base::Entity<T>::id)
        .add_property("created_at", &nix::base::Entity<T>::createdAt)
        .def("force_created_at", &nix::base::Entity<T>::forceCreatedAt)
        .add_property("updated_at", &nix::base::Entity<T>::updatedAt)
        .def("force_updated_at", &nix::base::Entity<T>::forceUpdatedAt);
}

template<typename T>
void export_named_entity(const std::string& name) {
    using namespace boost::python;

    std::string real_name = "__NamedEntity" + name;
    export_entity<T>(name);
    class_<nix::base::NamedEntity<T>, bases<nix::base::Entity<T>>>(real_name.c_str(), no_init);
}

}

#endif
