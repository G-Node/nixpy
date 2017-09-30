# -*- coding: utf-8 -*-
# Copyright © 2016, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from six import string_types
import re
from collections import Sequence
from ..exceptions import InvalidUnit


# Base32hex alphabet (RFC 4648)
ID_ALPHABET = "0123456789abcdefghijklmnopqrstuv"
# Unit scaling, SI only, substitutions for micro and ohm...
PREFIXES = "(Y|Z|E|P|T|G|M|k|h|da|d|c|m|u|n|p|f|a|z|y)"
UNITS = ("(m|g|s|A|K|mol|cd|Hz|N|Pa|J|W|C|V|F|S|Wb|T|H|lm|lx|Bq|Gy|Sv|kat|l|L|"
         "Ohm|%|dB|rad)")
POWER = "(\\^[+-]?[1-9]\\d*)"
PREFIX_FACTORS = {"y": 1.0e-24,
                  "z": 1.0e-21,
                  "a": 1.0e-18,
                  "f": 1.0e-15,
                  "p": 1.0e-12,
                  "n": 1.0e-9,
                  "u": 1.0e-6,
                  "m": 1.0e-3,
                  "c": 1.0e-2,
                  "d": 1.0e-1,
                  "da": 1.0e1,
                  "h": 1.0e2,
                  "k": 1.0e3,
                  "M": 1.0e6,
                  "G": 1.0e9,
                  "T": 1.0e12,
                  "P": 1.0e15,
                  "E": 1.0e18,
                  "Z": 1.0e21,
                  "Y": 1.0e24}


def sanitizer(unit):
    """
    Sanitizes a unit string. That is, it is de-blanked, and mu and µ symbols
    are changed to u for micro.

    :param unit: The unit that needs to be sanitized.

    :returns: the sanitized unit.
    :rtype: str
    """
    # micro = "\u03bc"
    micro = "µ"
    # mugr = "\u00b5"
    mugr = "μ"
    return unit.replace(" ", "").replace("mu", "u").\
        replace(micro, "u").replace(mugr, "u")


def is_si(unit):
    """
    Determines whether a unit is a recognized SI unit.

    :param unit: The unit that needs to be checked.

    :returns: True if the unit is an SI unit, false otherwise.
    :rtype: bool
    """
    return unit and (is_atomic(unit) or is_compound(unit))


def is_atomic(unit):
    """
    Checked whether a unit string represents an atomic si unit, i.e. not a
    combination.

    :param unit: The unit to be checked.

    :returns: True if unit is atomic, False otherwise.
    :rtype: bool
    """
    atomic_unit = re.compile(
        "^{prefix}?{unit}{power}?$".format(prefix=PREFIXES,
                                           unit=UNITS,
                                           power=POWER)
    )
    return atomic_unit.match(unit)


def is_compound(unit):
    """
    Checks whether a unit string represents a combination of SI units.

    :param unit: The unit string.

    :returns: True if the unit string represents a combination of SI units,
              False otherwise.
    :rtype: bool
    """
    atomic_unit = "{prefix}?{unit}{power}?".format(
        prefix=PREFIXES, unit=UNITS, power=POWER
    )
    compound_unit = re.compile(
        "({atomic}(\\*|/))+{atomic}".format(atomic=atomic_unit)
    )
    return unit and compound_unit.search(unit)


def scalable(unit_a, unit_b):
    """
    Checks whether units are scalable versions of the same SI unit.
    Method works on two lists and compares the corresponding units in both
    lists.

    :param unit_a: List of unit strings.
    :param unit_b: List of unit strings.

    :returns: True if all corresponding units are scalable.
    :rtype: bool
    """
    if (isinstance(unit_a, Sequence) and isinstance(unit_b, Sequence) and
            not isinstance(unit_a, string_types) and
            not isinstance(unit_b, string_types)):
        if len(unit_a) != len(unit_b):
            return False
        for a, b in zip(unit_a, unit_b):
            if not scalable(a, b):
                return False
        return True

    if not (is_si(unit_a) and is_si(unit_b)):
        return False

    a_prefix, a_unit, a_power = split(unit_a)
    b_prefix, b_unit, b_power = split(unit_b)
    if a_unit != b_unit or a_power != b_power:
        return False

    return True


def scaling(origin, destination):
    """
    Returns the scaling factor to convert from one unit to another.

    :param origin: The original unit string.
    :param destination: The destination unit string.

    :returns: The scaling factor.
    :rtype: double
    """
    scale = 1.0
    if not scalable(origin, destination):
        raise InvalidUnit(
            "Origin unit and destination unit are not scalable version of the "
            "same SI unit!",
            "nixio.util.scaling"
        )

    org_prefix, org_unit, org_power = split(origin)
    dest_prefix, dest_unit, dest_power = split(destination)

    if org_prefix == dest_prefix and org_power == dest_power:
        return scale
    if not dest_prefix and org_prefix:
        scale = PREFIX_FACTORS[org_prefix]
    elif not org_prefix and dest_prefix:
        scale = 1.0 / PREFIX_FACTORS[dest_prefix]
    elif not org_prefix and not dest_prefix:
        scale = PREFIX_FACTORS[org_prefix] / PREFIX_FACTORS[dest_prefix]

    if org_power:
        power = int(org_power)
        scale **= power

    return scale


def split(combined_unit):
    """
    Splits a unit string into magnitude prefix, the base unit, and the power.

    :param combined_unit: The unit string.

    :returns: A tuple of prefix, base unit, and power.
    :rtype: tuple
    """
    prefix_re = "(?P<prefix>{})".format(PREFIXES)
    unit_re = "(?P<unit>{})".format(UNITS)
    power_re = "(?P<power>{})".format(POWER)
    pup = re.compile(prefix_re + unit_re + power_re)
    pu = re.compile(prefix_re + unit_re)
    up = re.compile(unit_re + power_re)
    # u = re.compile(unit_re)
    # p = re.compile(prefix_re)

    match = pup.match(combined_unit)
    if match:
        prefix = match.group("prefix")
        unit = match.group("unit")
        power = match.group("power")[1:]
        return prefix, unit, power

    match = up.match(combined_unit)
    if match:
        prefix = ""
        unit = match.group("unit")
        power = match.group("power")[1:]
        return prefix, unit, power

    match = pu.match(combined_unit)
    if match:
        prefix = match.group("prefix")
        unit = match.group("unit")
        power = ""
        return prefix, unit, power

    prefix = ""
    unit = combined_unit
    power = ""
    return prefix, unit, power


def invert_power(unit):
    prefix, unit, power = split(unit)
    if not power:
        return prefix + unit + "^-1"
    if power[0] == "-":
        power = power[1:]
    else:
        power = "^-" + power
    return prefix + unit + "^" + power


def split_compound(compound_unit):
    """
    Splits a compound unit (like mV/Hz) into the atomic units.

    :param compound_unit: The unit string.

    :returns: A tuple containing the atomic units.
    :rtype: tuple
    """
    opt_pup = re.compile(PREFIXES + "?" + UNITS + POWER + "?")
    match = opt_pup.match(compound_unit)
    sep = ""
    atomic_units = []
    while match and (match.end() < len(match.string)):
        suffix = match.string[match.end():]
        suffix = suffix.replace(" ", "")
        unit = match.group(0)
        if sep == "/":
            atomic_units.append(invert_power(unit))
        else:
            atomic_units.append(unit)
        sep = suffix[0]
        match = opt_pup.match(suffix[1:])
    unit = match.group(0)
    if sep == "/":
        atomic_units.append(invert_power(unit))
    else:
        atomic_units.append(unit)
    return tuple(atomic_units)
