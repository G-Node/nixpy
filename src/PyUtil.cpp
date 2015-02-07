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
#include <docstrings.hpp>

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

std::vector<std::string> splitUnit(const std::string &unit) {
    std::string si, prefix, power;
    util::splitUnit(unit, prefix, si, power);
    return std::vector<std::string>{prefix, si, power};
}

std::vector<std::string> splitCompound(const std::string &unit) {
   std::vector<std::string> parts;
   util::splitCompoundUnit(unit, parts);
   return parts;
}

struct NameWrap {};


void PyUtil::do_export() {
  class_<UnitWrap> ("units")
  .def("sanitizer", util::unitSanitizer, doc::unit_sanitizer).staticmethod("sanitizer")
  .def("is_si", util::isSIUnit, doc::unit_is_si).staticmethod("is_si")
  .def("is_atomic", util::isAtomicSIUnit, doc::unit_is_atomic).staticmethod("is_atomic")
  .def("is_compound", util::isCompoundSIUnit, doc::unit_is_compound).staticmethod("is_compound")
  .def("scalable", &isScalableMultiUnits, doc::unit_scalable).staticmethod("scalable")
  .def("scaling", util::getSIScaling, doc::unit_scaling).staticmethod("scaling")
  .def("split", &splitUnit, doc::unit_split).staticmethod("split")
  .def("split_compound", &splitCompound, doc::unit_compound_split).staticmethod("split_compound")
  ;

  class_<NameWrap> ("names")
  .def("sanitizer", util::nameSanitizer).staticmethod("sanitizer")
  .def("check", util::nameCheck).staticmethod("check")
  .def("create_id", util::createId).staticmethod("create_id")
  ;
}

}
