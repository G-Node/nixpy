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

template<typename T>
std::string toStr(T number) {
    std::stringstream s;
    s << number;
    return s.str();
}

/**
 * Exports a specialisation of nix::base::Entity wich can be further used
 * as a subclass.
 *
 * @param type_name          Name of the type used for the specialisation.
 */
template<typename T>
struct PyEntity {

    static void do_export(const std::string& type_name) {
        using namespace boost::python;

        std::string real_name = "__Entity" + type_name;
        class_<nix::base::Entity<T>>(real_name.c_str(), no_init)
            .add_property("id", &nix::base::Entity<T>::id)
            .add_property("created_at", &nix::base::Entity<T>::createdAt)
            .def("force_created_at", &nix::base::Entity<T>::forceCreatedAt)
            .add_property("updated_at", &nix::base::Entity<T>::updatedAt)
            .def("force_updated_at", &nix::base::Entity<T>::forceUpdatedAt);
    }

};

template<typename T>
struct PyNamedEntity {

    DEF_OPT_SETTER(std::string, nix::base::NamedEntity<T>, definition, definition_setter)

    static void do_export(const std::string& type_name) {
        using namespace boost::python;

        std::string real_name = "__NamedEntity" + type_name;
        PyEntity<T>::do_export(type_name);
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


template<typename T>
struct PyEntityWithMetadata {

    DEF_ENT_GETTER(nix::Section, nix::base::EntityWithMetadata<T>, metadata, metadata_getter)
    DEF_OPT_SETTER(nix::Section, nix::base::EntityWithMetadata<T>, metadata, metadata_setter)

    static void do_export(const std::string& type_name) {
        using namespace boost::python;

        std::string real_name = "__EntityWithMetadata" + type_name;
        PyNamedEntity<T>::do_export(type_name);
        class_<nix::base::EntityWithMetadata<T>, bases<nix::base::NamedEntity<T>>>(real_name.c_str(), no_init)
            .add_property("metadata", &metadata_getter, &metadata_setter);
    }

};

template<typename T>
struct PyEntityWithSources {

    DEF_ENT_GETTER_BY(nix::Source, nix::base::EntityWithSources<T>, getSource, size_t, get_source_by_pos)
    DEF_ENT_GETTER_BY(nix::Source, nix::base::EntityWithSources<T>, getSource, std::string, get_source_by_id)

    static void do_export(const std::string& type_name) {
        using namespace boost::python;

        std::string real_name = "__EntityWithSources" + type_name;
        PyEntityWithMetadata<T>::do_export(type_name);
        class_<nix::base::EntityWithSources<T>, bases<nix::base::EntityWithMetadata<T>>>(real_name.c_str(), no_init)
            .def("_source_count", &nix::base::EntityWithSources<T>::sourceCount)
            .def("_has_source_by_id", CHECKER(std::string, nix::base::EntityWithSources<T>, hasSource))
            .def("_get_source_by_id", &get_source_by_id)
            .def("_get_source_by_pos", &get_source_by_pos)
            .def("_add_source_by_id", REF_SETTER(std::string, nix::base::EntityWithSources<T>, addSource))
            .def("_remove_source_by_id", REMOVER(std::string, nix::base::EntityWithSources<T>, removeSource));
    }
};


}

#endif
