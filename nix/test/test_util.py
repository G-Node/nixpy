#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in section and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import (absolute_import, division, print_function)#, unicode_literals)

import unittest
import numpy as np
from nix.core import names
from nix.core import units

class TestUtil(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_name_sanitizer(self):
        assert(names.sanitizer("validName") == "validName")
        assert(names.sanitizer("invalid/name") == "invalid_name")

    def test_name_check(self):
        assert(names.check("validName"))
        assert(not names.check("invalid/name"))

    def test_unit_sanitizer(self):
        assert(units.sanitizer("µV") == "uV")
        assert(units.sanitizer("muOhm") == "uOhm")

    def test_unit_is_si(self):
        assert(units.is_si('V'))
        assert(units.is_si('mV'))
        assert(units.is_si('kV'))
        assert(not units.is_si('Kv'))
        assert(not units.is_si('in'))
        assert(not units.is_si('pt'))
        assert(not units.is_si('ft'))
        assert(not units.is_si('yrd'))

    def test_unit_is_atomic(self):
        assert(units.is_atomic('mV'))
        assert(units.is_atomic('mV^2'))
        assert(not units.is_atomic('mV^2/Hz'))