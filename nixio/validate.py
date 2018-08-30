from __future__ import (absolute_import, division, print_function)
import numpy as np
from .util.units import *
from collections import OrderedDict


class Validate:

    def __init__(self, file):
        self.file = file
        self.errors = OrderedDict()
        self.errors['file_errors'] = []
        self.errors['blocks'] = []
        self.errors['sections'] = []
        self.error_count = 0  # only for file.py use, number will not be correct
        # if a function addressing same object is called more than once

    def form_dict(self):
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
                        'tags': [], 'multi_tags': [], 'errors': [], "obj_ref": blk}
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
                    self.errors['blocks'][bi]['data_arrays'][di]['dimensions'].append(dim_dict)

            for mi, mt in enumerate(blk.multi_tags):
                mt_dict = {'features': [], 'errors': [], "obj_ref": mt}
                self.errors['blocks'][bi]['multi_tags'].append(mt_dict)
                for fi, fea in enumerate(mt.features):
                    fea_dict = {'errors': [], "obj_ref": fea}
                    self.errors['blocks'][bi]['multi_tags'][mi]['features'].append(fea_dict)

            for ti, tag in enumerate(blk.tags):
                tag_dict = {'features': [], 'errors': [], "obj_ref": tag}
                self.errors['blocks'][bi]['tags'].append(tag_dict)
                for fi, fea in enumerate(tag.features):
                    fea_dict = {'errors': [], "obj_ref": fea}
                    self.errors['blocks'][bi]['tags'][ti]['features'].append(fea_dict)

    def check_file(self):

        file_err_list = []
        if not self.file.created_at:
            file_err_list.append("date is not set!")
        # will not check format as Error will be raised anyways
        # will not check version as Error will be raised
        # in nixpy no location attributes. This is checked in C++ version

        self.errors['file_errors'] = file_err_list
        self.error_count += len(file_err_list)
        return self.errors

    def check_blocks(self, block, blk_idx):
        blk_err_list = self.check_for_basics(block)

        self.errors['blocks'][blk_idx]['errors'] = blk_err_list
        self.error_count += len(blk_err_list)
        return self.errors

    def check_groups(self, group, grp_idx, blk_idx):
        grp_err_list = self.check_for_basics(group)

        if grp_err_list:
            self.errors['blocks'][blk_idx]['groups'][grp_idx]['errors'] = grp_err_list
            self.error_count += len(grp_err_list)
            return self.errors
        else:
            return None

    def check_data_arrays(self, da, da_idx, blk_idx):  # seperate da and dim checking
        da_error_list = []
        if self.check_for_basics(da):
            da_error_list.extend(self.check_for_basics(da))

        dim = da.shape
        len_dim = da.data_extent
        if dim != len_dim:
            da_error_list.append("Dimension mismatch")

        if da.dimensions:
            for dim in da.dimensions:
                if dim.dimension_type == 'range':
                    if len(dim.ticks) != len(da):
                        # if data_extent is used instead of len() tuple will be observed, eg (1200,)
                        da_error_list.append("In some Range Dimensions, the number"
                                             " of ticks differ from the data entries")
                if dim.dimension_type == 'set':
                    # same as above
                    if len(dim.labels) != len(da):
                        da_error_list.append("In some Set Dimensions, the number "
                                             "of labels differ from the data entries")

        unit = da.unit
        if unit and not is_si(unit):
            da_error_list.append("Invalid units")

        poly = da.polynom_coefficients
        ex_origin = da.expansion_origin
        if np.any(ex_origin):
            if not poly:
                da_error_list.append("Expansion origins exist but "
                                     "polynomial coefficients are missing")
        if np.any(poly):
            if not ex_origin:
                da_error_list.append("Polynomial coefficients exist" 
                                     " but expansion origins are missing")

        self.errors['blocks'][blk_idx]['data_arrays'][da_idx]['errors'] = da_error_list
        self.error_count += len(da_error_list)
        return self.errors

    def check_tag(self, tag, tag_idx, blk_idx):
        tag_err_list = []

        if not tag.position:
            tag_err_list.append("Position is not set!")
        if tag.references:
            # referenced da dimension and units should match the tag
            ndim = len(tag.references[0].shape)
            if tag.position:
                if len(tag.position) != ndim:
                    tag_err_list.append("Number of position "
                                        "and dimensionality of reference do not match")
            if tag.extent:
                if ndim != len(tag.extent):
                    tag_err_list.append("Number of extent "
                                        "and dimensionality of reference do not match")

            for ref in tag.references:
                unit_list = self.get_dim_units(ref)
                unit_list = [un for un in unit_list if un]
                dim_list = [dim for refer in tag.references for dim in refer.dimensions
                            if dim.dimension_type != 'set']
                if len(unit_list) != len(dim_list):
                    tag_err_list.append("Some dimensions of references have no units")
                for u in unit_list:
                    for tu in tag.units:
                        if not scalable(u, tu):
                            tag_err_list.append("References and tag units mismatched")
                            break
                    break

        for unit in tag.units:
            if not is_si(unit):
                tag_err_list.append('Invalid unit')

        self.errors['blocks'][blk_idx]['tags'][tag_idx]['errors'] = tag_err_list
        self.error_count += len(tag_err_list)
        return self.errors

    def check_multi_tag(self, mt, mt_idx, blk_idx):
        mt_err_list = []

        if not mt.positions:
            mt_err_list.append("Position is not set!")  # no test for this
        else:
            if len(mt.positions.shape) > 2:
                mt_err_list.append("Positions should not have more than 2 dimensions")
        if mt.extents:
            if len(mt.extents.shape) > 2:
                mt_err_list.append("Extents should not have more than 2 dimensions")
            if mt.positions.shape != mt.extents.shape:
                # not sure what index should be given to shape
                mt_err_list.append("Number of entries in positions and extents do not match")
        if mt.references:
            ref_ndim = len(mt.references[0].shape)  # assume all references have same shape
            if ref_ndim > 1 and len(mt.positions.shape) == 1:
                mt_err_list.append("The number of reference and position"
                                   " entries do not match")
            elif len(mt.positions.shape) == 2 and mt.positions.shape[1] != ref_ndim:
                mt_err_list.append("The number of reference and position"
                                   " entries do not match")
            if mt.extents:
                if len(mt.extents.shape) == 1 and ref_ndim > 1:
                    mt_err_list.append("The number of reference and extent"
                                       " entries do not match")
                elif len(mt.extents.shape) == 2 and mt.extents.shape[1] != ref_ndim:
                    # should we add a function for limiting extent dim to <= 2
                    mt_err_list.append("The number of reference and extent"
                                       " entries do not match")
        for unit in mt.units:
            if not is_si(unit):
                mt_err_list.append("Invalid unit")
                continue
            for ref in mt.references:
                u_list = self.get_dim_units(ref)
                for u in u_list:
                    if not scalable(u, unit):
                        mt_err_list.append("References and multi_tag units mismatched")
                        break

        self.errors['blocks'][blk_idx]['multi_tags'][mt_idx]['errors'] = mt_err_list
        self.error_count += len(mt_err_list)
        return self.errors

    def check_section(self, section, sec_idx):

        self.errors['sections'][sec_idx]['errors'] = self.check_for_basics(section)
        self.error_count += len(self.check_for_basics(section))

        return self.errors

    def check_property(self, prop, prop_idx, sec_idx):
        prop_err_list = []

        if not prop.name:
            prop_err_list.append("Name is not set!")
        if prop.values and not prop.unit:
            prop_err_list.append("Unit is not set")
        if prop.unit and not is_si(prop.unit):
            prop_err_list.append("Unit is not valid!")
        self.errors['sections'][sec_idx]['props'][prop_idx]['errors'] = prop_err_list
        self.error_count += len(prop_err_list)
        return self.errors

    def check_features(self, feat, parent, blk_idx, tag_idx, fea_idx):

        fea_err_list = []
        # will raise RuntimeError for both, actually no need to check
        if not feat.link_type:
            fea_err_list.append("Linked type is not set!")
        if not feat.data:
            fea_err_list.append("Data is not set")

        self.errors['blocks'][blk_idx][parent][tag_idx]['features']\
                                [fea_idx]['errors'] = fea_err_list
        self.error_count += len(fea_err_list)
        return self.errors

    def check_sources(self, src, blk_idx):
        if self.check_for_basics(src):
            self.errors['blocks'][blk_idx]['sources'] = self.check_for_basics(src)
            self.error_count += len(self.check_for_basics(src))
            return self.errors
        else:
            return None

    def check_dim(self, dimen):  # call it in file after the index problem is fixed
        # call it in other check dim function/ dont call alone
        if dimen.index and dimen.index > 0:
            return None
        else:
            return 'index must > 0'

    def check_range_dim(self, r_dim, dim_idx, da_idx, blk_idx):
        rdim_err_list = []

        if self.check_dim(r_dim):
            rdim_err_list.append(self.check_dim(r_dim))

        if not r_dim.ticks:
            rdim_err_list.append("Ticks need to be set for range dimensions")
        elif not all(r_dim.ticks[i] <= r_dim.ticks[i+1] for i in range(len(r_dim.ticks)-1)):
            rdim_err_list.append("Ticks are not sorted!")
        if r_dim.dimension_type != 'range':
            rdim_err_list.append("Dimension type is not correct!")

        # sorting is already covered in the dimensions.py file
        if r_dim.unit:
            if not is_atomic(r_dim.unit):
                rdim_err_list.append("Unit must be atomic, not composite!")

        self.errors['blocks'][blk_idx]['data_arrays']\
            [da_idx]['dimensions'][dim_idx]['errors'] = rdim_err_list
        self.error_count += len(rdim_err_list)
        return self.errors

    def check_set_dim(self, set_dim, dim_idx, da_idx, blk_idx):

        if self.check_dim(set_dim):
            self.errors['blocks'][blk_idx]['data_arrays'][da_idx]['dimensions'][dim_idx] \
                ['errors'].append(self.check_dim(set_dim))
            self.error_count += 1
        if set_dim.dimension_type != 'set':
            self.errors['blocks'][blk_idx]['data_arrays'][da_idx]['dimensions'][dim_idx]\
                                ['errors'].append("Dimension type is not correct!")
            self.error_count += 1
        return self.errors

    def check_sampled_dim(self, sam_dim, dim_idx, da_idx, blk_idx):
        sdim_err_list = []

        if self.check_dim(sam_dim):
            sdim_err_list.append(self.check_dim(sam_dim))

        if sam_dim.sampling_interval < 0:
            sdim_err_list.append("SamplingInterval is not set to valid value (> 0)!")

        if sam_dim.dimension_type != 'sample':
            sdim_err_list.append("Dimension type is not correct!")

        if sam_dim.offset and not sam_dim.unit:
            sdim_err_list.append("Offset is set, but no unit set!")  # validity check below

        if sam_dim.unit:
            if not is_atomic(sam_dim.unit):
                sdim_err_list.append("Unit must be atomic, not composite!")

        self.errors['blocks'][blk_idx]['data_arrays']\
            [da_idx]['dimensions'][dim_idx]['errors'] = sdim_err_list
        self.error_count += len(sdim_err_list)
        return self.errors

    def check_for_basics(self, entity):
        basic_check_list = []
        if not entity.type:
            basic_check_list.append("Type of {} is missing".format(type(entity).__name__))
        if not entity.id:
            basic_check_list.append("ID of {} is missing".format(type(entity).__name__))
        if not entity.name:
            basic_check_list.append("Name of {} is missing".format(type(entity).__name__))

        return basic_check_list

    def get_dim_units(self, data_arrays):
        unit_list = []
        for dim in data_arrays.dimensions:
            if dim.dimension_type == 'range':
                unit_list.append(dim.unit)
            if dim.dimension_type == 'sample':
                unit_list.append(dim.unit)
            if dim.dimension_type == 'set':
                pass
        return unit_list




