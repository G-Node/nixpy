// Copyright (c) 2014, German Neuroinformatics Node (G-Node)
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
#include <docstrings.hpp>

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
            .add_property("id", &nix::base::Entity<T>::id, doc::entity_id)
            .add_property("created_at", &nix::base::Entity<T>::createdAt, doc::entity_crated_at)
            .def("force_created_at", &nix::base::Entity<T>::forceCreatedAt, doc::entity_force_created_at)
            .add_property("updated_at", &nix::base::Entity<T>::updatedAt, doc::entity_updated_at)
            .def("force_updated_at", &nix::base::Entity<T>::forceUpdatedAt, doc::entity_force_updated_at);
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
                          doc::entity_name)
            .add_property("type",
                          GETTER(std::string, nix::base::NamedEntity<T>, type),
                          REF_SETTER(std::string, nix::base::NamedEntity<T>, type),
                          doc::entity_type)
            .add_property("definition",
                          OPT_GETTER(std::string, nix::base::NamedEntity<T>, definition),
                          &definition_setter,
                          doc::entity_definition);
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
            .add_property("metadata", &metadata_getter, &metadata_setter, doc::entity_metadata);
    }

};

template<typename T>
struct PyEntityWithSources {

    DEF_ENT_GETTER_BY(nix::Source, nix::base::EntityWithSources<T>, getSource, size_t, get_source_by_pos)
    DEF_ENT_GETTER_BY(nix::Source, nix::base::EntityWithSources<T>, getSource, std::string, get_source_by_id)

    static void do_export(const std::string& type_name) {
        using namespace boost::python;

        // TODO create mixin for all bases of EntityWithSources
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

struct PyResult {
    static void do_export();
};

struct PyBlock {
    static void do_export();
};

struct PyFile {
    static void do_export();
};

struct PyProperty {
    static void do_export();
};

struct PySection {
    static void do_export();
};

struct PyValue {
    static void do_export();
};

struct PySource {
    static void do_export();
};

struct PyDataArray {
    static void do_export();
};

struct PyDataSet {
    static void do_export();
};

struct PyDimensions {
    static void do_export();
};

struct PyFeature {
    static void do_export();
};

struct PyTag {
    static void do_export();
};

struct PyMultiTag {
    static void do_export();
};

}

#endif
