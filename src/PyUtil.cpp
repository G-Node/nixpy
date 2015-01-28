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

void PyUtil::do_export() {
  def("name_sanitizer", util::nameSanitizer);

}

}
