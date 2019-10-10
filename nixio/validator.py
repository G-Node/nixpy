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
from .dimensions import (RangeDimension, SampledDimension, SetDimension,
                         DimensionType)
try:
    from collections.abc import OrderedDict
except ImportError:
    from collections import OrderedDict


class Validator(object):

    def __init__(self, file):
        self.file = file
        self.errors = OrderedDict()
        self.errors['file_errors'] = []
        self.errors['blocks'] = []
        self.errors['sections'] = []
        # only for file.py use, number will not be correct
        # if a function addressing same object is called more than once
        self.error_count = 0

    def form_dict(self):
        """
        Form a empty dict that has same structure as the data tree in the file.
        """
        file = self.file
        self.error_count = 0

        for si, sec in enumerate(file.find_sections()):
            prop_dict = {'errors': [], 'props': [], "obj_ref": sec}
            self.errors['sections'].append(prop_dict)

            for pi, prop in enumerate(sec.props):
                pe_dict = {'errors': [], "obj_ref": prop}
                self.errors['sections'][si]['props'].append(pe_dict)

        for bi, blk in enumerate(file.blocks):
            blk_dict = {'sources': [], 'groups': [], 'data_arrays': [],
                        'tags': [], 'multi_tags': [], 'errors': [],
                        "obj_ref": blk}
            self.errors['blocks'].append(blk_dict)
            OrderedDict(self.errors)

            for gi, grp in enumerate(blk.groups):
                grp_dict = {'errors': [], "obj_ref": grp}
                self.errors['blocks'][bi]['groups'].append(grp_dict)

            for di, da in enumerate(blk.data_arrays):
                d = {'dimensions': [], 'errors': [], "obj_ref": da}
                self.errors['blocks'][bi]['data_arrays'].append(d)
                for dim_idx, dim in enumerate(da.dimensions):
                    dim_dict = {'errors': [], "obj_ref": dim}
                    da = self.errors['blocks'][bi]['data_arrays'][di]
                    da['dimensions'].append(dim_dict)

            for mi, mt in enumerate(blk.multi_tags):
                mt_dict = {'features': [], 'errors': [], "obj_ref": mt}
                self.errors['blocks'][bi]['multi_tags'].append(mt_dict)
                for fi, fea in enumerate(mt.features):
                    fea_dict = {'errors': [], "obj_ref": fea}
                    mtag = self.errors['blocks'][bi]['multi_tags'][mi]
                    mtag['features'].append(fea_dict)

            for ti, tag in enumerate(blk.tags):
                tag_dict = {'features': [], 'errors': [], "obj_ref": tag}
                self.errors['blocks'][bi]['tags'].append(tag_dict)
                for fi, fea in enumerate(tag.features):
                    fea_dict = {'errors': [], "obj_ref": fea}
                    tag = self.errors['blocks'][bi]['tags'][ti]
                    tag['features'].append(fea_dict)


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
        results["errors"][nixfile] = ["date is not set"]

    file_warnings = list()
    if not nixfile.version:
        file_warnings.append("version is not set")
    if not nixfile.format:
        file_warnings.append("format is not set")
    if file_warnings:
        results["warnings"][nixfile] = file_warnings

    def update_results(obj, errors, warnings):
        if errors:
            results["errors"][obj] = errors
        if warnings:
            results["warnings"][obj] = warnings

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

            # Features

        # MultiTags

            # Features

        # Sources

    # Sections

        # Properties
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
        errors.append("data type is not set")

    if len(da.dimensions) != len(da.data_extent):
        errors.append("data dimensionality does not match number of defined "
                      "dimensions")

    if da.unit and not units.is_si(da.unit):
        warnings.append("unit is not SI or composite of SI units")

    if da.polynom_coefficients and not da.expansion_origin:
        warnings.append("polynomial coefficients for calibration are set, "
                        "but expansion origin is missing")
    elif da.expansion_origin and not da.polynom_coefficients:
        warnings.append("expansion origin for calibration is set, "
                        "but polynomial coefficients are missing")
    dimtypemap = {
        DimensionType.Range: RangeDimension,
        DimensionType.Sample: SampledDimension,
        DimensionType.Set: SetDimension,
    }

    for idx, (dim, datalen) in enumerate(zip(da.dimensions, da.shape), 1):
        if not dim.index or dim.index <= 0:
            errors.append("index for dimension {} is not set to a valid value "
                          "(index > 0)".format(idx))
        elif dim.index != idx:
            errors.append("index for dimension {} is set to incorrect "
                          "value {}".format(idx, da.index))
        if not isinstance(dim, dimtypemap[dim.dimension_type]):
            errors.append("dimension_type attribute for dimension "
                          "{} does not match "
                          "Dimension object type".format(idx))
        if isinstance(dim, RangeDimension):
            if dim.ticks is not None and len(dim.ticks) != datalen:
                # if ticks is None or empty, it will be reported by the
                # dimension check function
                errors.append("number of ticks in RangeDimension ({}) "
                              "differs from the number of data entries "
                              "along the corresponding "
                              "data dimension".format(idx))
            dim_errors, dim_warnings = check_range_dimension(dim, idx)
        elif isinstance(dim, SampledDimension):
            dim_errors, dim_warnings = check_sampled_dimension(dim, idx)
        elif isinstance(dim, SetDimension):
            if dim.labels and len(dim.labels) != datalen:
                # empty labels is allowed
                errors.append("number of labels in SetDimension ({}) "
                              "differs from the number of data entries "
                              "along the corresponding "
                              "data dimension".format(idx))
            dim_errors, dim_warnings = check_set_dimension(dim, idx)
        errors.extend(dim_errors)
        warnings.extend(dim_warnings)
    return errors, warnings


def check_tag(self, tag, tag_idx, blk_idx):
    """
    Check if the file meets the NIX requirements at the tag level.

    :returns: The error dictionary with errors appended on Tag level
    """
    tag_err_list = []

    if not tag.position:
        tag_err_list.append("position is not set")
    if tag.references:
        # referenced da dimension and units should match the tag
        ndim = len(tag.references[0].shape)
        if tag.position:
            if len(tag.position) != ndim:
                tag_err_list.append(
                    "number of position and dimensionality of reference "
                    "do not match"
                )
        if tag.extent:
            if ndim != len(tag.extent):
                tag_err_list.append("number of extent and dimensionality "
                                    "of reference do not match")

        for ref in tag.references:
            unit_list = self.get_dim_units(ref)
            unit_list = [un for un in unit_list if un]
            dim_list = [dim for refer in tag.references
                        for dim in refer.dimensions
                        if dim.dimension_type != DimensionType.Set]
            if len(unit_list) != len(dim_list):
                tag_err_list.append(
                    "some dimensions of references have no units"
                )
            for u in unit_list:
                for tu in tag.units:
                    if not units.scalable(u, tu):
                        tag_err_list.append(
                            "references and tag units mismatched"
                        )
                        break
                break

    for unit in tag.units:
        if not units.is_si(unit):
            tag_err_list.append('Invalid unit')

    tag = self.errors['blocks'][blk_idx]['tags'][tag_idx]
    tag['errors'] = tag_err_list
    self.error_count += len(tag_err_list)
    return self.errors

def check_multi_tag(self, mt, mt_idx, blk_idx):
    mt_err_list = []

    if not mt.positions:
        mt_err_list.append("position is not set")  # no test for this
    else:
        if len(mt.positions.shape) > 2:
            mt_err_list.append(
                "Positions should not have more than 2 dimensions"
            )
    if mt.extents:
        if len(mt.extents.shape) > 2:
            mt_err_list.append(
                "Extents should not have more than 2 dimensions"
            )
        if mt.positions.shape != mt.extents.shape:
            # not sure what index should be given to shape
            mt_err_list.append(
                "Number of entries in positions and extents do not match"
            )
    if mt.references:
        # assume all references have same shape
        ref_ndim = len(mt.references[0].shape)
        if ref_ndim > 1 and len(mt.positions.shape) == 1:
            mt_err_list.append("The number of reference and position"
                               " entries do not match")
        elif (len(mt.positions.shape) == 2 and
              mt.positions.shape[1] != ref_ndim):
            mt_err_list.append("The number of reference and position"
                               " entries do not match")
        if mt.extents:
            if len(mt.extents.shape) == 1 and ref_ndim > 1:
                mt_err_list.append("The number of reference and extent"
                                   " entries do not match")
            elif (len(mt.extents.shape) == 2 and
                  mt.extents.shape[1] != ref_ndim):
                # should we add a function for limiting extent dim to <= 2
                mt_err_list.append("The number of reference and extent"
                                   " entries do not match")
    for unit in mt.units:
        if not units.is_si(unit):
            mt_err_list.append("Invalid unit")
            continue
        for ref in mt.references:
            u_list = self.get_dim_units(ref)
            for u in u_list:
                if not units.scalable(u, unit):
                    mt_err_list.append(
                        "References and multi_tag units mismatched"
                    )
                    break

    mtag = self.errors['blocks'][blk_idx]['multi_tags'][mt_idx]
    mtag['errors'] = mt_err_list
    self.error_count += len(mt_err_list)
    return self.errors

def check_section(self, section, sec_idx):
    """
    Check if the file meets the NIX requirements at the section level.

    :returns: The error dictionary with errors appended on section level
    """
    sec = self.errors['sections'][sec_idx]
    sec['errors'] = self.check_for_basics(section)
    self.error_count += len(self.check_for_basics(section))

    return self.errors

def check_property(self, prop, prop_idx, sec_idx):
    prop_err_list = []

    if not prop.name:
        prop_err_list.append("Name is not set")
    if prop.values and not prop.unit:
        prop_err_list.append("Unit is not set")
    if prop.unit and not units.is_si(prop.unit):
        prop_err_list.append("Unit is not valid")
    prop = self.errors['sections'][sec_idx]['props'][prop_idx]
    prop['errors'] = prop_err_list
    self.error_count += len(prop_err_list)
    return self.errors

def check_features(self, feat, parent, blk_idx, tag_idx, fea_idx):
    """
    Check if the file meets the NIX requirements at the feature level.

    :returns: The error dictionary with errors appended on feature level
    """
    fea_err_list = []
    # will raise RuntimeError for both, actually no need to check
    if not feat.link_type:
        fea_err_list.append("Linked type is not set")
    if not feat.data:
        fea_err_list.append("Data is not set")

    tag = self.errors['blocks'][blk_idx][parent][tag_idx]
    tag['features'][fea_idx]['errors'] = fea_err_list
    self.error_count += len(fea_err_list)
    return self.errors

def check_sources(self, src, blk_idx):
    """
    Check if the file meets the NIX requirements at the source level.

    :returns: The error dictionary with errors appended on source level
    """
    if self.check_for_basics(src):
        blk = self.errors['blocks'][blk_idx]
        blk['sources'] = self.check_for_basics(src)
        self.error_count += len(self.check_for_basics(src))
        return self.errors
    return None


def check_range_dimension(dim, idx):
    """
    Validate a RangeDimension and return all errors and warnings.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = list()
    warnings = list()

    if not dim.ticks:
        errors.append("ticks for dimension {} are not set".format(idx))
    elif not all(ti < tj for ti, tj in zip(dim.ticks[:-1], dim.ticks[1:])):
        errors.append("ticks for dimension {} are not sorted".format(idx))

    if dim.unit and not units.is_atomic(dim.unit):
        errors.append("unit for dimension {} is set but it is not an "
                      "atomic SI unit "
                      "(Note: composite units are not supported)".format(idx))
    return errors, warnings


def check_set_dimension(dim, idx):
    """
    Validate a SetDimension and return all errors and warnings.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    return list(), list()


def check_sampled_dimension(dim, idx):
    """
    Validate a SetDimension and return all errors and warnings.

    :returns: A list of 'errors' and a list of 'warnings'
    """
    errors = list()
    warnings = list()

    if dim.sampling_interval:
        errors.append("sampling interval for dimension {} "
                      "is not set".format(idx))
    elif dim.sampling_interval < 0:
        errors.append("sampling interval for dimension {} "
                      "is not valid (interval > 0)".format(idx))

    if dim.unit:
        if units.is_atomic(dim.unit):
            errors.append("unit for dimension {} is set but it is not an "
                          "atomic SI unit (Note: composite units are "
                          "not supported)".format(idx))
    else:
        if dim.offset:
            warnings.append("offset for dimension {} is set, "
                            "but no valid unit is set".format(idx))
    return errors, warnings


def check_entity(entity):
    """
    General NIX entity validator
    """
    errors = []
    if not entity.type:
        errors.append("no type set")
    if not entity.id:
        errors.append("no ID set")
    if not entity.name:
        errors.append("no name set")
    if not entity.created_at:
        errors.append("date not set")
    return errors

def get_dim_units(self, data_arrays):
    """
    Help function to collect the units of the dimensions of a data array
    """
    unit_list = []
    for dim in data_arrays.dimensions:
        if dim.dimension_type == DimensionType.Range or\
                dim.dimension_type == DimensionType.Sample:
            unit_list.append(dim.unit)
    return unit_list
