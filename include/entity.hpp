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
 *                      Converntion __EntitySpecialClass
 */
template<typename T>
void export_entity(const std::string& name) {
    boost::python::class_<nix::base::Entity<T>>(name.c_str(), boost::python::no_init)
        .add_property("id", &nix::base::Entity<T>::id)
        .add_property("created_at", &nix::base::Entity<T>::createdAt)
        .def("force_created_at", &nix::base::Entity<T>::forceCreatedAt)
        .add_property("updated_at", &nix::base::Entity<T>::updatedAt)
        .def("force_updated_at", &nix::base::Entity<T>::forceUpdatedAt);
}

}

#endif
