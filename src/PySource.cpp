// Copyright (c) 2014, German Neuroinformatics Node (G-Node)
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted under the terms of the BSD License. See
// LICENSE source in the root of the Project.

#include <boost/python.hpp>
#include <boost/optional.hpp>

#include <nix.hpp>

#include <accessors.hpp>
#include <transmorgify.hpp>

#include <PyEntity.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

// getter for Source

boost::optional<Source> getSourceById(const Source& source, const std::string& id) {
    Source src = source.getSource(id);

    return src ? boost::optional<Source>(src) : boost::none;
}

boost::optional<Source> getSourceByPos(const Source& source, size_t index) {
    Source src = source.getSource(index);

    return src ? boost::optional<Source>(src) : boost::none;
}

void PySource::do_export() {

    PyEntityWithMetadata<base::ISource>::do_export("Source");

    class_<Source, bases<base::EntityWithMetadata<base::ISource>>>("Source")
        // Source
        .def("create_source", &Source::createSource)
        .def("_source_count", &Source::sourceCount)
        .def("_has_source_by_id", CHECKER(std::string, Source, hasSource))
        .def("_get_source_by_id", getSourceById)
        .def("_get_source_by_pos", getSourceByPos)
        .def("_delete_source_by_id", REMOVER(std::string, Source, deleteSource))
        // Inverse search
        .add_property("referring_data_arrays", &Source::referringDataArrays)
        .add_property("referring_tags", &Source::referringTags)
        .add_property("referring_multi_tags", &Source::referringMultiTags)
        // Other
        .def("__str__", &toStr<Source>)
        .def("__repr__", &toStr<Source>)
        ;

    to_python_converter<std::vector<Source>, vector_transmogrify<Source>>();
    to_python_converter<boost::optional<Source>, option_transmogrify<Source>>();
    option_transmogrify<Source>::register_from_python();
}

}
