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
#include <iostream>

#include <PyEntity.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

// getter for Section

boost::optional<Section> getSectionById(const Section& section, const std::string& id) {
    Section sec = section.getSection(id);

    return sec ? boost::optional<Section>(sec) : boost::none;
}

boost::optional<Section> getSectionByPos(const Section& section, size_t index) {
    Section sec = section.getSection(index);

    return sec ? boost::optional<Section>(sec) : boost::none;
}

// Property

Property createProperty(Section& sec, const std::string& name, PyObject* obj) {
    extract<DataType> ext_type(obj);
    if (ext_type.check()) {
        return sec.createProperty(name, ext_type());
    }

    extract<Value> ext_val(obj);
    if (ext_val.check()) {
        return sec.createProperty(name, ext_val());
    }

    extract<std::vector<Value>> ext_vec(obj);
    if (ext_vec.check()) {
        return sec.createProperty(name, ext_vec());
    }

    throw new std::runtime_error("Second parameter must be a Value, list of Value or DataType");
}

boost::optional<Property> getPropertyById(const Section& section, const std::string& id) {
    Property prop = section.getProperty(id);

    return prop ? boost::optional<Property>(prop) : boost::none;
}

boost::optional<Property> getPropertyByPos(const Section& section, size_t index) {
    Property prop = section.getProperty(index);

    return prop ? boost::optional<Property>(prop) : boost::none;
}

boost::optional<Property> getPropertyByName(const Section& section, const std::string& name) {
    Property prop = section.getPropertyByName(name);

    return prop ? boost::optional<Property>(prop) : boost::none;
}

// Repository

void setRepository(Section& sec, const boost::optional<std::string>& str) {
    if (str)
        sec.repository(*str);
    else
        sec.repository(boost::none);
}

// Mapping

void setMapping(Section& sec, const boost::optional<std::string>& str) {
    if (str)
        sec.mapping(*str);
    else
        sec.mapping(boost::none);
}

// Link

void setLink(Section& section, const boost::optional<Section>& link) {
    if (link && *link)
        section.link(*link);
    else
        section.link(boost::none);
}

boost::optional<Section> getLink(const Section& sec) {
    Section link = sec.link();
    return link ? boost::optional<Section>(link) : boost::none;
}

// Parent

boost::optional<Section> getParent(const Section& sec) {
    Section parent = sec.parent();
    return parent ? boost::optional<Section>(parent) : boost::none;
}


void PySection::do_export() {

    PyNamedEntity<base::ISection>::do_export("Section");
    class_<Section, bases<base::NamedEntity<base::ISection>>>("Section")
        // Properties
        .add_property("repository",
                      OPT_GETTER(std::string, Section, repository),
                      setRepository,
                      doc::section_repository)
        .add_property("mapping",
                      OPT_GETTER(std::string, Section, mapping),
                      setMapping,
                      doc::section_mapping)
        .add_property("link", getLink, setLink, doc::section_link)
        // Section
        .add_property("parent", getParent, doc::section_parent)
        .def("create_section", &Section::createSection,
             doc::section_create_section)
        .def("_section_count", &Section::sectionCount)
        .def("_get_section_by_id", &getSectionById)
        .def("_get_section_by_pos", &getSectionByPos)
        .def("_delete_section_by_id", REMOVER(std::string, nix::Section, deleteSection))
        // Property
        .def("create_property", createProperty)
        .def("has_property_by_name", &Section::hasPropertyByName,
             doc::section_has_property_by_name)
        .def("get_property_by_name", getPropertyByName,
             doc::section_get_property_by_name)
        .def("_property_count", &Section::propertyCount)
        .def("_get_property_by_id", &getPropertyById)
        .def("_get_property_by_pos", &getPropertyByPos)
        .def("_delete_property_by_id", REMOVER(std::string, nix::Section, deleteProperty))
        .def("inherited_properties", &Section::inheritedProperties)
        // Other
        .def("__str__", &toStr<Section>)
        .def("__repr__", &toStr<Section>)
        ;

    to_python_converter<std::vector<Section>, vector_transmogrify<Section>>();
    to_python_converter<boost::optional<Section>, option_transmogrify<Section>>();
    option_transmogrify<Section>::register_from_python();
}

}
