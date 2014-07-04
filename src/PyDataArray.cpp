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

void setLabel(DataArray& da, const boost::optional<std::string>& label) {
    if (label)
        da.label(*label);
    else
        da.label(boost::none);
}

// Unit

void setUnit(DataArray& da, const boost::optional<std::string> &unit) {
    if (unit)
        da.unit(*unit);
    else
        da.unit(boost::none);
}

// Expansion origin

void setExpansionOrigin(DataArray& da, const boost::optional<double>& eo) {
    if (eo)
        da.expansionOrigin(*eo);
    else
        da.expansionOrigin(boost::none);
}

// Polynom coefficients

void setPolynomCoefficients(DataArray& da, const std::vector<double>& pc) {
    if (!pc.empty())
        da.polynomCoefficients(pc);
    else
        da.polynomCoefficients(boost::none);
}

// Data

std::vector<double> getData(DataArray& da) {
    std::vector<double> data;
    da.getData(data);
    return data;
}

void setData(DataArray& da, const std::vector<double>& data) {
    if (!data.empty())
        da.setData(data);
    else
        // TODO How do I remove data?
        da.dataExtent(NDSize());
}

// Dimensions

PyObject* getDimension(const DataArray& da, size_t index) {
    Dimension dim = da.getDimension(index);
    SetDimension set;
    RangeDimension range;
    SampledDimension sample;
    DimensionType type = dim.dimensionType();

    switch(type) {
        case DimensionType::Set:
            set = dim;
            return incref(object(set).ptr());
        case DimensionType::Range:
            range = dim;
            return incref(object(range).ptr());
        case DimensionType::Sample:
            sample = dim;
            return incref(object(sample).ptr());
        default:
            Py_RETURN_NONE;
    }
}

void PyDataArray::do_export() {

    PyEntityWithSources<base::IDataArray>::do_export("DataArray");
    class_<DataArray, bases<base::EntityWithSources<base::IDataArray>>>("DataArray")
        .add_property("label",
                      OPT_GETTER(std::string, DataArray, label),
                      setLabel)
        .add_property("unit",
                      OPT_GETTER(std::string, DataArray, unit),
                      setUnit)
        .add_property("expansion_origin",
                      OPT_GETTER(double, DataArray, expansionOrigin),
                      setExpansionOrigin)
        .add_property("polynom_coefficients",
                      GETTER(std::vector<double>, DataArray, polynomCoefficients),
                      setPolynomCoefficients)
        .add_property("data_extent",
                      GETTER(NDSize, DataArray, dataExtent))
        // Data
        .add_property("data_type", &DataArray::dataType)
        .add_property("data", getData, setData)
        .def("has_data", &DataArray::hasData)
        // Dimensions
        .def("create_set_dimension", &DataArray::createSetDimension)
        .def("create_sampled_dimension", &DataArray::createSampledDimension)
        .def("create_reange_dimension", &DataArray::createRangeDimension)
        .def("append_set_dimension", &DataArray::appendSetDimension)
        .def("append_sampled_dimension", &DataArray::appendSampledDimension)
        .def("append_range_dimension", &DataArray::appendRangeDimension)
        .def("_dimension_count", &DataArray::dimensionCount)
        .def("_delete_dimension_by_pos", &DataArray::deleteDimension)
        .def("_get_dimension_by_pos", getDimension)
        // Other
        .def("__str__", &toStr<DataArray>)
        .def("__repr__", &toStr<DataArray>)
        ;


    to_python_converter<std::vector<DataArray>, vector_transmogrify<DataArray>>();
    vector_transmogrify<DataArray>::register_from_python();



    to_python_converter<boost::optional<DataArray>, option_transmogrify<DataArray>>();
}

}
