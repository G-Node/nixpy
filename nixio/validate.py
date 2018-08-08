from __future__ import (absolute_import, division, print_function)
import os
import shutil
import h5py
import numpy as np
import quantities as pq
import nixio as nix
from .exceptions import *
from .util.units import *


class Validate():

    def __init__(self, file):
        self.file = file
        self.errors = {'files': [], 'blocks': []}

    def form_dict(self):
        file = self.file

        for bi, blk in enumerate(file.blocks):
            blk_dict = {'groups': [], 'data_arrays': [],
                        'tags': [], 'multi_tags': [], 'blk_err': []}
            self.errors['blocks'].append(blk_dict)

            for gi, da in enumerate(blk.data_arrays):
                d = {'dimensions': [] , 'da_err': []}
                self.errors['blocks'][bi]['data_arrays'].append(d)

    def check_file(self):

        file_err_list = []
        if not self.file.created_at: file_err_list.append("date is not set!")
        if not self.file.format: file_err_list.append("format is not set!")
        if not self.file.version: file_err_list.append("version is not set!")
        # in nixpy no location attributes. This is checked in C++ version

        if file_err_list:
            self.errors['files'].append(file_err_list)
            return self.errors
        else:
            return None

    def check_blocks(self, blocks, blk_idx):

        blk_err_list = self.check_for_basics(blocks, blk_idx)

        if blk_err_list:
            self.errors['blocks'][blk_idx]['blk_err'].append(blk_err_list)
            return self.errors
        else:
            return None

    def check_groups(self, groups, grp_idx, blk_idx):

        grp_err_list = self.check_for_basics(groups, grp_idx)

        if grp_err_list:
            self.errors['blocks'][blk_idx]['groups'].append(grp_err_list)
            return self.errors
        else:
            return None

    def check_data_array(self, da, da_idx, blk_idx):  # seperate da and dim checking

        da_error_list = []
        if self.check_for_basics(da,da_idx):
            da_error_list.extend(self.check_for_basics(da,da_idx))
        else:
            pass
        if da == []:
            da_error_list.append("No empty data_array")

        dim = da.shape
        len_dim = da.data_extent
        if dim != len_dim:
            da_error_list.append("dimension mismatch")


        if da.dimensions:
            for dim in da.dimensions:
                if dim.dimension_type == 'range':
                    if len(dim.ticks) != len(da): # or should I use da.data_extent
                        da_error_list.append("in some Range Dimensions, the number"
                                             " of ticks differ from the data entries")
                if dim.dimension_type == 'set': # don't know why only check set dim
                    if len(dim.labels) != len(da):
                        da_error_list.append("in some Set Dimensions, the number "
                                             "of ticks differ from the data entries")

        unit = da.unit
        if not is_si(unit):
            da_error_list.append("invalid units")

        poly = da.polynom_coefficients
        ex_origin = da.expansion_origin
        if np.any(ex_origin):
            if not poly:
                da_error_list.append("Expansion origins exist but "
                                 "polynomial coefficients are missing!")
        if poly and not ex_origin:
            da_error_list.append("Polynomial coefficients exist" \
                              " but expansion origins are missing")

        if da_error_list:
            self.errors['blocks'][blk_idx]['data_arra' \
                                           'ys'][da_idx]['da_err'].append(da_error_list)
            return self.errors
        else:
            return None

    def check_tag(self, tag):
        tag_err_list = []

        for blk in self.file.blocks:
            for grp in blk.groups:
                for tag in grp.tags:
                    if not tag.position:
                        a = "Position is not set!"
                    if tag.references:
                        # referenced da dimension and units should match the tag
                        if tag.references.size != len(tag.position):
                            err_msg = "number of data do not match"
                        if tag.extent:
                            if tag.positions.shape[1] != len(tag.references):
                                err_msg2 = "number of data do not match"
                            if tag.references.size != tag.extent.size:
                                err_msg3 = "number of data do not match"
                    if tag.units:
                        if not is_si(tag.units):
                            b = "It is not a valid unit"
                        if not tag.references.units:
                            err_msg1 = "references need to have units"
                            continue
                        if tag.references.units != tag.units:
                            c = "Units unmatched"

    def check_multi_tag(self):
        mt_err_list = []

        for blk in self.file.blocks:
            for grp in blk.groups:
                for mt in grp.multi_tags:
                    if not mt.positions:
                        a = "Position is not set!"
                        continue
                    if mt.extents:
                        if mt.positions.shape[1] != len(mt.extents):
                            err_msg = "No of entries in positions and extents do not match"
                    if mt.references:
                        if mt.positions.shape[1] != len(mt.references):
                            err_msg1 = "The number of entries do not match"
                        if mt.extents:
                            if len(mt.references) != len(mt.extents):
                                err_msg2 = "Entries unmatch"
                    if mt.units:
                        if not is_si(mt.units):
                            b = "It is not a valid unit"
                        if mt.references.units != mt.units:
                            err_msg3 = "Units not match"

    def check_section(self):
        for meta in self.file.metadata:  # this part may be replaced by check_for_basics
            if not meta.name:
                err_msg1 = "Section must have names"
            if not meta.id:
                err_msg2 = "Section must have id"
            if not meta.type:
                err_msg3 = "Section must have type"
            for prop in meta.property:
                if prop.values and not prop.unit:
                    b = "Why there is no unit?"
                    continue
                if prop.unit and not is_si(prop.unit):
                    a = "The unit is not valid!"

    def check_features(self):
        pass

    def check_sources(self):
        self.check_for_basics()

    def check_dim(self, dimen, da_idx, blk_idx):  # call it in file after the index problem is fixed
        if dimen.index:
            return None
        else:
            self.errors['blocks'][blk_idx]['data_arrays'][da_idx]['dimensions'].append('index must > 0')
            return self.errors

    def check_range_dim(self, r_dim, da_idx, blk_idx):
        rdim_err_list = []

        if not r_dim.ticks:
            rdim_err_list.append("ticks need to be set for range dimensions")
        if type(r_dim).__name__ != "RangeDimension" :
            rdim_err_list.append("dimension type is not correct!")

        # sorting!
        if r_dim.unit:
            if not is_atomic(r_dim.unit):
                rdim_err_list.append("unit must be atomic, not composite!")

        if rdim_err_list:
            self.errors['blocks'][blk_idx]['data_arrays']\
                [da_idx]['dimensions'].append(rdim_err_list)
            return self.errors
        else:
            return None

    def check_set_dim(self, set_dim, da_idx, blk_idx):
        if type(set_dim).__name__ != "SetDimension":
            self.errors['blocks'][blk_idx]['data_arrays'][da_idx] \
                ['dimensions'].append("dimension type is not correct!")
            return self.errors
        else:
            return None

    def check_sampled_dim(self, sam_dim, da_idx, blk_idx):
        sdim_err_list = []

        if sam_dim.sampling_interval < 0:
            sdim_err_list.append("samplingInterval is not set to valid value (> 0)!")

        if type(sam_dim).__name__ != "SampledDimension":
            sdim_err_list.append("dimension type is not correct!")

        if sam_dim.offset and not sam_dim.unit:
            sdim_err_list.append("offset is set, but no valid unit set!")

        if sam_dim.unit:
            if not is_atomic(sam_dim.unit):
                sdim_err_list.append("unit must be atomic, not composite!")

        if sdim_err_list:
            self.errors['blocks'][blk_idx]['data_arrays']\
                [da_idx]['dimensions'].append(sdim_err_list)
            return self.errors
        else:
            return None


    def check_for_basics(self,entity, idx):
        basic_check_list = []
        a = b = c = ''
        if not entity.type:
            a = "Type of {} {} is missing".format(type(entity).__name__, idx)
            basic_check_list.append(a)
        if not entity.id:
            b = "ID of {} {} is missing".format(type(entity).__name__, idx)
            basic_check_list.append(b)
        if not entity.name:
            c = "Name of {} {} is missing".format(type(entity).__name__, idx)
            basic_check_list.append(c)
        if a == b == c == '':
            return None
        else:
            return basic_check_list








