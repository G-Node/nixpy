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
#include <nix/util/util.hpp>

#include <accessors.hpp>
#include <transmorgify.hpp>

#include <PyUtil.hpp>

using namespace nix;
using namespace boost::python;

namespace nixpy {

struct UnitWrap {};

bool isScalableSingleUnit(const std::string &unitA, const std::string &unitB) {
    return util::isScalable(unitA, unitB);
}

bool isScalableMultiUnits(const std::vector<std::string> &unitsA, const std::vector<std::string> &unitsB) {
    return util::isScalable(unitsA, unitsB);
}

struct NameWrap {};


void PyUtil::do_export() {
  class_<UnitWrap> ("unit_helper")
  .def("unit_sanitizer", util::unitSanitizer).staticmethod("unit_sanitizer")
  .def("is_si_unit", util::isSIUnit).staticmethod("is_si_unit")
  .def("is_atomic_unit", util::isAtomicSIUnit).staticmethod("is_atomic_unit")
  .def("is_compound_unit", util::isCompoundSIUnit).staticmethod("is_compound_unit")
  .def("is_scalable", &isScalableMultiUnits).staticmethod("is_scalable")
  .def("scaling", util::getSIScaling).staticmethod("scaling")
  ;

  class_<NameWrap> ("name_helper")
  .def("name_sanitizer", util::nameSanitizer).staticmethod("name_sanitizer")
  .def("name_check", util::nameCheck).staticmethod("name_check")
  .def("create_id", util::createId).staticmethod("create_id")
  ;
}

}
