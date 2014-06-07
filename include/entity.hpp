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
#include <accessors.hpp>

namespace nixpy {

/**
 * Exports a specialisation of nix::base::Entity wich can be further used
 * as a subclass.
 *
 * @param type_name          Name of the type used for the specialisation.
 */
template<typename T>
void export_entity(const std::string& type_name) {
    using namespace boost::python;

    std::string real_name = "__Entity" + type_name;
    class_<nix::base::Entity<T>>(real_name.c_str(), no_init)
        .add_property("id", &nix::base::Entity<T>::id)
        .add_property("created_at", &nix::base::Entity<T>::createdAt)
        .def("force_created_at", &nix::base::Entity<T>::forceCreatedAt)
        .add_property("updated_at", &nix::base::Entity<T>::updatedAt)
        .def("force_updated_at", &nix::base::Entity<T>::forceUpdatedAt);
}

template<typename T>
struct named_entity {

    DEF_OPT_SETTER(std::string, nix::base::NamedEntity<T>, definition, definition_setter)

    static void do_export(const std::string& type_name) {
        using namespace boost::python;

        std::string real_name = "__NamedEntity" + type_name;
        export_entity<T>(type_name);
        class_<nix::base::NamedEntity<T>, bases<nix::base::Entity<T>>>(real_name.c_str(), no_init)
            .add_property("name",
                        GETTER(std::string, nix::base::NamedEntity<T>, name),
                        REF_SETTER(std::string, nix::base::NamedEntity<T>, name))
            .add_property("type",
                        GETTER(std::string, nix::base::NamedEntity<T>, type),
                        REF_SETTER(std::string, nix::base::NamedEntity<T>, type))
            .add_property("definition",
                          OPT_GETTER(std::string, nix::base::NamedEntity<T>, definition),
                          &definition_setter);
    }
};

}

#endif
