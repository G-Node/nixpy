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
#include <PySection.hpp>

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

Property createProperty(Section& sec, const std::string& name, const std::vector<Value>& values = std::vector<Value>()) {
    if (values.size() == 0)
        return sec.createProperty(name);
    else
        return sec.createProperty(name, values);
}

BOOST_PYTHON_FUNCTION_OVERLOADS(createPropertyOverloads, createProperty, 2, 3)

boost::optional<Property> getPropertyById(const Section& section, const std::string& id) {
    Property prop = section.getProperty(id);

    return prop ? boost::optional<Property>(prop) : boost::none;
}

boost::optional<Property> getPropertyByPos(const Section& section, size_t index) {
    Property prop = section.getProperty(index);

    return prop ? boost::optional<Property>(prop) : boost::none;
}

boost::optional<Property> getPropertyWithName(const Section& section, const std::string& name) {
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
                      setRepository)
        .add_property("mapping",
                      OPT_GETTER(std::string, Section, mapping),
                      setMapping)
        .add_property("link", getLink, setLink)
        // Section
        .add_property("parent", getParent)
        .def("create_section", &Section::createSection)
        .def("_section_count", &Section::sectionCount)
        .def("_get_section_by_id", &getSectionById)
        .def("_get_section_by_pos", &getSectionByPos)
        .def("_delete_section_by_id", REMOVER(std::string, nix::Section, deleteSection))
        // Property
        .def("create_property", createProperty, createPropertyOverloads())
        .def("has_property_with_name", &Section::hasPropertyWithName)
        .def("get_property_with_name", getPropertyWithName)
        .def("_property_count", &Section::propertyCount)
        .def("_get_property_by_id", &getPropertyById)
        .def("_get_property_by_pos", &getPropertyByPos)
        .def("_delete_property_by_id", REMOVER(std::string, nix::Section, deleteProperty))
        .def("_inherited_properties", &Section::inheritedProperties)
        // Other
        .def("__str__", &toStr<Section>)
        .def("__repr__", &toStr<Section>)
        ;

    to_python_converter<std::vector<Section>, vector_transmogrify<Section>>();
    to_python_converter<boost::optional<Section>, option_transmogrify<Section>>();
    option_transmogrify<Section>::register_from_python();
}

}
