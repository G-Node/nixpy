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


// Label

void setSampledDimensionLabel(SampledDimension& dim, const boost::optional<std::string>& label) {
    if (label)
        dim.label(*label);
    else
        dim.label(boost::none);
}

void setRangeDimensionLabel(RangeDimension& dim, const boost::optional<std::string>& label) {
    if (label)
        dim.label(*label);
    else
        dim.label(boost::none);
}

void setSetDimensionLabels(SetDimension& dim, const std::vector<std::string>& labels) {
    if (!labels.empty())
        dim.labels(labels);
    else
        dim.labels(boost::none);
}

// Unit

void setSampledDimensionUnit(SampledDimension& dim, const boost::optional<std::string>& unit) {
    if (unit)
        dim.unit(*unit);
    else
        dim.unit(boost::none);
}

void setRangeDimensionUnit(RangeDimension& dim, const boost::optional<std::string>& unit) {
    if (unit)
        dim.unit(*unit);
    else
        dim.unit(boost::none);
}

// Offset

void setSampledDimensionOffset(SampledDimension& dim, const boost::optional<double>& offset) {
    if (offset)
        dim.offset(*offset);
    else
        dim.offset(boost::none);
}

std::vector<double> getSampledDimensionAxis1(SampledDimension& dim, const size_t count) {
    return dim.axis(count);
}

std::vector<double> getSampledDimensionAxis2(SampledDimension& dim, const size_t count,
					    const size_t start_index) {
    return dim.axis(count, start_index);
}

std::vector<double> getRangeDimensionAxis1(RangeDimension& dim, const size_t count) {
    return dim.axis(count);
}

std::vector<double> getRangeDimensionAxis2(RangeDimension& dim, const size_t count,
					    const size_t start_index) {
    return dim.axis(count, start_index);
}

void PyDimensions::do_export() {

    enum_<DimensionType>("DimensionType")
        .value("Sample", DimensionType::Sample)
        .value("Range" , DimensionType::Range)
        .value("Set"   , DimensionType::Set)
        ;

    class_<SampledDimension>("SampledDimension")
        .add_property("index", &SampledDimension::index)
        .add_property("dimension_type", &SampledDimension::dimensionType)
        .add_property("label",
                      OPT_GETTER(std::string, SampledDimension, label),
                      setSampledDimensionLabel)
        .add_property("unit",
                      OPT_GETTER(std::string, SampledDimension, unit),
                      setSampledDimensionUnit)
        .add_property("sampling_interval",
                      GETTER(double, SampledDimension, samplingInterval),
                      SETTER(double, SampledDimension, samplingInterval))
        .add_property("offset",
                      OPT_GETTER(double, SampledDimension, offset),
                      setSampledDimensionOffset)
        .def("position_at", &SampledDimension::positionAt, doc::sampled_dimension_position_at)
        .def("index_of", &SampledDimension::indexOf, doc::sampled_dimension_index_of)
        .def("axis", getSampledDimensionAxis1, doc::sampled_dimension_axis)
        .def("axis", getSampledDimensionAxis2, doc::sampled_dimension_axis)
        ;

    class_<RangeDimension>("RangeDimension")
        .add_property("index", &RangeDimension::index)
        .add_property("dimension_type", &RangeDimension::dimensionType)
        .add_property("label",
                      OPT_GETTER(std::string, RangeDimension, label),
                      setRangeDimensionLabel)
        .add_property("unit",
                      OPT_GETTER(std::string, RangeDimension, unit),
                      setRangeDimensionUnit)
        .add_property("ticks",
                      GETTER(std::vector<double>, RangeDimension, ticks),
                      REF_SETTER(std::vector<double>, RangeDimension, ticks))
        .def("index_of", &RangeDimension::indexOf, doc::range_dimension_index_of)
        .def("tick_at", &RangeDimension::tickAt, doc::range_dimension_tick_at)
        .def("axis", getRangeDimensionAxis1, doc::range_dimension_axis)
        .def("axis", getRangeDimensionAxis2, doc::range_dimension_axis)
        ;

    class_<SetDimension>("SetDimension")
        .add_property("index", &SetDimension::index)
        .add_property("dimension_type", &SetDimension::dimensionType)
        .add_property("labels",
                      GETTER(std::vector<std::string>, SetDimension, labels),
                      setSetDimensionLabels)
        ;
}

}
