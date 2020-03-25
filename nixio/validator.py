# -*- coding: utf-8 -*-
# Copyright © 2019, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
from __future__ import (absolute_import, division, print_function)
from .util import units
from .dimension_type import DimensionType


class ValidationError(object):
    """
    Static class for defining validation error messages
    """
    NoName = "no name set"
    NoType = "no type set"
    NoDate = "date is not set"
    NoDataType = "data type is not set"
    NoID = "no ID set"
    DimensionMismatch = ("data dimensionality does not match number of "
                         "defined dimensions")
    InvalidDimensionIndex = ("index for dimension {} is not set to a valid "
                             "value (index > 0)")
    IncorrectDimensionIndex = ("index for dimension {} is set to incorrect "
                               "value {}")
    DimensionTypeMismatch = ("dimension_type attribute for dimension "
                             "{} does not match Dimension object type")
    RangeDimTicksMismatch = ("number of ticks in RangeDimension ({}) "
                             "differs from the number of data entries "
                             "along the corresponding data dimension")
    SetDimLabelsMismatch = ("number of labels in SetDimension ({}) "
                            "differs from the number of data entries "
                            "along the corresponding data dimension")
    NoPosition = "position is not set"
    PositionDimensionMismatch = ("number of entries in position does not "
                                 "match number of dimensions in all "
                                 "referenced DataArrays")
    ExtentDimensionMismatch = ("number of entries in extent does not match "
                               "number of dimensions in all referenced "
                               "DataArrays")
    PositionExtentMismatch = ("number of entries in position and extent "
                              "do not match")
    ReferenceUnitsMismatch = ("some of the referenced DataArrays' dimensions "
                              "don't have units where the Tag has; "
                              "make sure that all references have the same "
                              "number of dimensions as the Tag has units "
                              "and that each dimension has a unit set")
    ReferenceUnitsIncompatible = ("some of the referenced DataArrays' "
                                  "dimensions have units that are not "
                                  "convertible to the units set in the Tag "
                                  "(Note: composite units are not supported)")
    InvalidUnit = ("unit is invalid: not an atomic SI "
                   "(Note: composite units are not supported)")
    NoPositions = "positions are not set"
    PositionsDimensionMismatch = ("number of entries (in 2nd dim) in "
                                  "positions does not match number of "
                                  "dimensions in all referenced DataArrays")
    ExtentsDimensionMismatch = ("number of entries (in 2nd dim) in extents "
                                "does not match number of dimensions in all "
                                "referenced DataArrays")
    PositionsExtentsMismatch = ("number of entries in positions and extents "
                                "do not match")
    NoTicks = "ticks for dimension {} are not set"
    UnsortedTicks = "ticks for dimension {} are not sorted"
    InvalidDimensionUnit = ("unit for dimension {} is set but it is not an "
                            "atomic SI unit "
                            "(Note: composite units are not supported)")
    NoSamplingInterval = ("sampling interval for dimension {} "
                          "is not set")
    InvalidSamplingInterval = ("sampling interval for dimension {} "
                               "is not valid (interval > 0)")
    DataFrameMismatch = ("referenced data frame for dimension {} does "
                         "not have the same row count as the data array")
    NoData = "data is not set"
    NoLinkType = "link_type is not set"


class ValidationWarning(object):
    NoVersion = "version is not set"
    NoFormat = "format is not set"
    NoFileID = "file ID is not set"
    InvalidUnit = "unit is not SI or composite of SI units"
    NoExpansionOrigin = ("polynomial coefficients for calibration are set, "
                         "but expansion origin is missing")
    NoPolynomialCoefficients = ("expansion origin for calibration is set, "
                                "but polynomial coefficients are missing")
    OffsetNoUnit = ("offset for dimension {} is set, "
                    "but no valid unit is set")
    NoUnit = "unit is not set"


def check_file(nixfile):
    """
    Validate a NIX file and all contained objects and return all errors and
    warnings for each individual object.

    :returns: A nested dictionary of errors and warnings. Each subdictionary
    is indexed by the object with values describing the error or warning.
    :rtype: Dictionary
    """
    results = {"errors": dict(), "warnings": dict()}
    if not nixfile.created_at:
        results["errors"][nixfile] = [ValidationError.NoDate]

    file_warnings = list()
    if not nixfile.version:
        file_warnings.append(ValidationWarning.NoVersion)
    if not nixfile.format:
        file_warnings.append(ValidationWarning.NoFormat)
    if not nixfile.id and nixfile.version and nixfile.version >= (1, 2, 0):
        file_warnings.append(ValidationWarning.NoFileID)
    if file_warnings:
        results["warnings"][nixfile] = file_warnings

    def update_results(obj, errors, warnings):
        if errors:
            results["errors"][obj] = errors
        if warnings:
            results["warnings"][obj] = warnings

    # Sources
    def traverse_sources(sources):
        # for recursively checking a source tree
        for source in sources:
            src_errors, src_warnings = check_source(source)
            update_results(source, src_errors, src_warnings)
            traverse_sources(source.sources)

    # Sections
    def traverse_sections(sections):
        # for recursively checking a metadata tree
        for section in sections:
            sec_errors, sec_warnings = check_section(section)
            update_results(section, sec_errors, sec_warnings)
            traverse_sections(section.sections)

    # Blocks
    for block in nixfile.blocks:
        blk_errors, blk_warnings = check_block(block)
        update_results(block, blk_errors, blk_warnings)

        # Groups
        for group in block.groups:
            grp_errors, grp_warnings = check_group(group)
            update_results(group, grp_errors, grp_warnings)

        # DataArrays
        for da in block.data_arrays:
            da_errors, da_warnings = check_data_array(da)
            update_results(da, da_errors, da_warnings)

        # Tags
        for tag in block.tags:
            tag_errors, tag_warnings = check_tag(tag)
            update_results(tag, tag_errors, tag_warnings)

        # MultiTags
        for mtag in block.multi_tags:
            mtag_errors, mtag_warnings = check_multi_tag(mtag)
            update_results(mtag, mtag_errors, mtag_warnings)

        traverse_sources(block.sources)

    traverse_sections(nixfile.sections)

    return results


def check_block(block):
    """
    Validate a Block and return all errors and warnings for the block and each
    individual contained object.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = check_entity(block)
    return errors, list()


def check_group(group):
    """
    Validate a Group and return all errors and warnings.
    Does not check contained objects.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = check_entity(group)
    return errors, list()


def check_data_array(da):
    """
    Validate a DataArray and its Dimensions and return all errors and warnings.
    Errors and warnings about Dimension objects are included in the DataArray
    errors and warnings lists.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = check_entity(da)
    warnings = list()

    if not da.data_type:
        errors.append(ValidationError.NoDataType)

    if len(da.dimensions) != len(da.shape):
        errors.append(ValidationError.DimensionMismatch)

    if da.unit and not units.is_si(da.unit):
        warnings.append(ValidationWarning.InvalidUnit)

    if da.polynom_coefficients and not da.expansion_origin:
        warnings.append(ValidationWarning.NoExpansionOrigin)
    elif da.expansion_origin and not da.polynom_coefficients:
        warnings.append(ValidationWarning.NoPolynomialCoefficients)

    for idx, (dim, datalen) in enumerate(zip(da.dimensions, da.shape), 1):
        if not dim.index or dim.index <= 0:
            errors.append(ValidationError.InvalidDimensionIndex.format(idx))
        elif dim.index != idx:
            errors.append(
                ValidationError.IncorrectDimensionIndex.format(idx, dim.index)
            )
        if dim.dimension_type == DimensionType.Range:
            if dim.ticks is not None and len(dim.ticks) != datalen:
                # if ticks is None or empty, it will be reported by the
                # dimension check function
                errors.append(
                    ValidationError.RangeDimTicksMismatch.format(idx)
                )
            dim_errors, dim_warnings = check_range_dimension(dim, idx)
        elif dim.dimension_type == DimensionType.Sample:
            dim_errors, dim_warnings = check_sampled_dimension(dim, idx)
        elif dim.dimension_type == DimensionType.Set:
            if dim.labels and len(dim.labels) != datalen:
                # empty labels is allowed
                errors.append(ValidationError.SetDimLabelsMismatch.format(idx))
            dim_errors, dim_warnings = check_set_dimension(dim, idx)
        elif dim.dimension_type == DimensionType.DataFrame:
            df_len = dim.data_frame.row_count()
            if df_len != da.shape[0]:
                dim_errors, dim_warnings = check_df_dimension(dim, idx)
        errors.extend(dim_errors)
        warnings.extend(dim_warnings)
    return errors, warnings


def check_tag(tag):
    """
    Validate a Tag and its Features and return all errors and warnings.
    Errors and warnings about Features are included in the Tag errors and
    warnings lists.

    For Features, only the basic Entity requirements, LinkType, and the
    existence of a referenced DataArray are checked.  The linked DataArray is
    not checked for validity (see check_data_array() for those validation
    checks).

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = check_entity(tag)
    warnings = list()

    if not tag.position:
        errors.append(ValidationError.NoPosition)
    if tag.references:
        posdim = len(tag.position)
        if any(posdim != len(da.shape) for da in tag.references):
            errors.append(ValidationError.PositionDimensionMismatch)
        if tag.extent:
            extlen = len(tag.extent)
            if extlen != posdim:
                errors.append(ValidationError.PositionExtentMismatch)
            if any(extlen != len(da.shape) for da in tag.references):
                errors.append(ValidationError.ExtentDimensionMismatch)

        refs_units = [get_dim_units(da) for da in tag.references]
        if any(len(ru) != len(tag.units) for ru in refs_units):
            errors.append(ValidationError.ReferenceUnitsMismatch)

        if not tag_units_match_refs_units(tag.units, refs_units):
            errors.append(ValidationError.ReferenceUnitsIncompatible)

    if any(not units.is_si(u) for u in tag.units if u):
        errors.append(ValidationError.InvalidUnit)

    for idx, feat in enumerate(tag.features):
        feat_errors = check_feature(feat, idx)
        errors.extend(feat_errors)

    return errors, warnings


def check_multi_tag(mtag):
    """
    Validate a MultiTag and its Features and return all errors and warnings.
    Errors and warnings about Features are included in the MultiTag errors and
    warnings lists.

    For Features, only the basic Entity requirements, LinkType, and the
    existence of a referenced DataArray are checked.  The linked DataArray is
    not checked for validity (see check_data_array() for those validation
    checks).

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = check_entity(mtag)
    warnings = list()

    if not mtag.positions:
        errors.append(ValidationError.NoPositions)
    if mtag.references:
        if len(mtag.positions.shape) == 1:
            posdim = 1
        else:
            posdim = mtag.positions.shape[1]
        # New error for len(mtag.positions.shape) > 2
        if any(posdim != len(da.shape) for da in mtag.references):
            errors.append(ValidationError.PositionsDimensionMismatch)
        if mtag.extents:
            if mtag.positions.shape != mtag.extents.shape:
                errors.append(ValidationError.PositionsExtentsMismatch)
            if len(mtag.extents.shape) == 1:
                extdim = 1
            else:
                extdim = mtag.extents.shape[1]
            if any(extdim != len(da.shape) for da in mtag.references):
                errors.append(ValidationError.ExtentsDimensionMismatch)

        refs_units = [get_dim_units(da) for da in mtag.references]
        if any(len(ru) != len(mtag.units) for ru in refs_units):
            errors.append(ValidationError.ReferenceUnitsMismatch)

        if not tag_units_match_refs_units(mtag.units, refs_units):
            errors.append(ValidationError.ReferenceUnitsIncompatible)

    if any(not units.is_si(u) for u in mtag.units if u):
        errors.append(ValidationError.InvalidUnit)

    for idx, feat in enumerate(mtag.features):
        feat_errors = check_feature(feat, idx)
        errors.extend(feat_errors)

    return errors, warnings


def check_feature(feat, idx):
    """
    Validate a Feature and return all errors.

    :returns: A list of 'errors'
    """
    errors = list()
    if not feat.id:
        errors.append("feature {}: {}".format(idx, ValidationError.NoID))
    if feat.created_at is None:
        errors.append("feature {}: {}".format(idx, ValidationError.NoDate))
    if not feat.data:
        errors.append("feature {}: {}".format(idx, ValidationError.NoData))
    if not feat.link_type:
        errors.append("feature {}: {}".format(idx, ValidationError.NoLinkType))
    return errors


def check_section(section):
    """
    Validate a Section and its Properties return all errors and warnings.

    Errors and warnings about Properties are included in the Section errors and
    warnings lists.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = check_entity(section)
    warnings = list()
    for idx, prop in enumerate(section.props):
        prop_errors, prop_warnings = check_property(prop, idx)
        errors.extend(prop_errors)
        warnings.extend(prop_warnings)

    return errors, warnings


def check_property(prop, idx):
    """
    Validate a Property and return all errors.

    :returns: A list of 'errors' and 'warnings'
    """
    errors = list()
    warnings = list()
    if not prop.id:
        errors.append("property {}: {}".format(idx, ValidationError.NoID))
    if not prop.name:
        errors.append("property {}: {}".format(idx, ValidationError.NoName))
    if not prop.unit:
        warnings.append("property {}: {}".format(idx,
                                                 ValidationWarning.NoUnit))
    return errors, warnings


def check_source(source):
    """
    Validate a Source and return all errors and warnings.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = check_entity(source)
    return errors, list()


def check_range_dimension(dim, idx):
    """
    Validate a RangeDimension and return all errors and warnings.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = list()
    warnings = list()

    if not dim.ticks:
        errors.append(ValidationError.NoTicks.format(idx))
    elif not all(ti < tj for ti, tj in zip(dim.ticks[:-1], dim.ticks[1:])):
        errors.append(ValidationError.UnsortedTicks.format(idx))

    if dim.unit and not units.is_atomic(dim.unit):
        errors.append(ValidationError.InvalidDimensionUnit.format(idx))
    return errors, warnings


def check_set_dimension(dim, idx):
    """
    Validate a SetDimension and return all errors and warnings.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    return list(), list()


def check_sampled_dimension(dim, idx):
    """
    Validate a SampledDimension and return all errors and warnings.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = list()
    warnings = list()

    if not dim.sampling_interval:
        errors.append(ValidationError.NoSamplingInterval.format(idx))
    elif dim.sampling_interval < 0:
        errors.append(ValidationError.InvalidSamplingInterval.format(idx))

    if dim.unit:
        if not units.is_atomic(dim.unit):
            errors.append(ValidationError.InvalidDimensionUnit.format(idx))
    else:
        if dim.offset:
            warnings.append(ValidationWarning.OffsetNoUnit.format(idx))
    return errors, warnings


def check_df_dimension(dim, idx):
    """
    Validate a DataFrameDimension and return all errors and warnings.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = [ValidationError.DataFrameNotMatch.format(idx)]
    warnings = list()
    return errors, warnings


def check_entity(entity):
    """
    General NIX entity validator
    """
    errors = []
    if not entity.type:
        errors.append(ValidationError.NoType)
    if not entity.id:
        errors.append(ValidationError.NoID)
    if not entity.name:
        errors.append(ValidationError.NoName)
    if entity.created_at is None:
        errors.append(ValidationError.NoDate)
    return errors


def get_dim_units(data_array):
    """
    Helper function to collect the units of the dimensions of a data array
    """
    unit_list = []
    for dim in data_array.dimensions:
        if (dim.dimension_type == DimensionType.Range or
                dim.dimension_type == DimensionType.Sample):
            unit_list.append(dim.unit if dim.unit else "")
        elif dim.dimension_type == DimensionType.Set:
            unit_list.append("")
    return unit_list


def tag_units_match_refs_units(tag_units, refs_units):
    for ref in refs_units:
        for ru, tu in zip(tag_units, ref):
            if ru == "" and tu == "":
                continue
            if not units.scalable(ru, tu):
                return False
    return True
