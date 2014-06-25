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
        // Section
        .add_property("parent", &Section::parent)
        .def("create_section", &Section::createSection)
        .def("_section_count", &Section::sectionCount)
        .def("_get_section_by_id", &getSectionById)
        .def("_get_section_by_pos", &getSectionByPos)
        .def("_delete_section_by_id", REMOVER(std::string, nix::Section, deleteSection))
        // Other
        .def("__str__", &toStr<Section>)
        .def("__repr__", &toStr<Section>)
        .def(self == self)
        ;

    to_python_converter<std::vector<Section>, vector_transmogrify<Section>>();
    to_python_converter<boost::optional<Section>, option_transmogrify<Section>>();
}

}
