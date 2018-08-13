from __future__ import (absolute_import, division, print_function)
import os
import h5py
import numpy as np
import quantities as pq
import nixio as nix
from .exceptions import *
from .util.units import *
from collections import OrderedDict

class Validate():

    def __init__(self, file):
        self.file = file
        self.errors = OrderedDict()
        self.errors['files'] = []
        self.errors['blocks'] = []
        self.errors['sections'] = []

    def form_dict(self):
        file = self.file

        for si, sec in enumerate(file.find_sections()):
            prop_dict = {'props': []}
            self.errors['sections'].append(prop_dict)

        for bi, blk in enumerate(file.blocks):
            blk_dict = {'sources':[], 'groups': [], 'data_arrays': [],
                        'tags': [], 'multi_tags': [], 'blk_err': []}
            self.errors['blocks'].append(blk_dict)
            OrderedDict(self.errors)

            for gi, da in enumerate(blk.data_arrays):
                d = {'dimensions': [] , 'da_err': []}
                self.errors['blocks'][bi]['data_arrays'].append(d)

            for mi, mt in enumerate(blk.multi_tags):
                mt_dict = {'features': [], 'mt_err': []}
                self.errors['blocks'][bi]['multi_tags'].append(mt_dict)

            for ti, tag in enumerate(blk.tags):
                tag_dict = {'features': [], 'tag_err': []}
                self.errors['blocks'][bi]['tags'].append(tag_dict)

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

        blk_err_list = self.check_for_basics(blocks)

        if blk_err_list:
            self.errors['blocks'][blk_idx]['blk_err'].append(blk_err_list)
            return self.errors
        else:
            return None

    def check_groups(self, groups, grp_idx, blk_idx):

        grp_err_list = self.check_for_basics(groups)

        if grp_err_list:
            self.errors['blocks'][blk_idx]['groups'].append(grp_err_list)
            return self.errors
        else:
            return None

    def check_data_array(self, da, da_idx, blk_idx):  # seperate da and dim checking

        da_error_list = []
        if self.check_for_basics(da):
            da_error_list.extend(self.check_for_basics(da))
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

    def check_tag(self, tag, tag_idx, blk_idx):
        tag_err_list = []

        if not tag.position:
            tag_err_list.append("Position is not set!")
        if tag.references:
            # referenced da dimension and units should match the tag
            if tag.references.size != len(tag.position):
                tag_err_list.append("number of data do not match")
            if tag.extent:
                if tag.positions.shape[1] != len(tag.references):
                    tag_err_list.append("number of data do not match")
                if tag.references.size != tag.extent.size:
                    tag_err_list.append("number of data do not match")
        if tag.units:
            if not is_si(tag.units):
                tag_err_list.append("It is not a valid unit")
            if not tag.references.units:
                tag_err_list.append("references need to have units")
            elif tag.references.units != tag.units:
                    tag_err_list.append("Units unmatched")

        if tag_err_list:
            self.errors['blocks'][blk_idx]['tags'][tag_idx]['tag' \
                                                            '_err'].append(tag_err_list)
            return self.errors
        else:
            return None

    def check_multi_tag(self, mt, mt_idx, blk_idx):
        mt_err_list = []

        if not mt.positions:
            mt_err_list.append("Position is not set!")
        if mt.extents:
            if mt.positions.shape[0] != mt.extents.shape[0]:  # not sure if correct
                # not sure what index should be given to shape
                mt_err_list.append("No of entries in positions and extents do not match")
        if mt.references:
            if len(mt.positions) != len(mt.references):  # not sure if correct
                mt_err_list.append("The number of entries do not match")
            if mt.extents:
                if len(mt.references) != len(mt.extents):
                    mt_err_list.append("Entries unmatch")
        if mt.units:
            if not is_si(mt.units):
                mt_err_list.append("It is not a valid unit")
            if mt.references.units != mt.units:
                mt_err_list.append("Units not match")

        if mt_err_list:
            self.errors['blocks'][blk_idx]['multi_tags'][mt_idx]['mt' \
                                                            '_err'].append(mt_err_list)
            return self.errors
        else:
            return None

    def check_section(self, section):
        if self.check_for_basics(section):
            self.errors['sections'].append(self.check_for_basics(section))
            return self.errors
        else:
            return None

    def check_property(self, prop, sec_idx):
        prop_err_list = []

        if prop.values and not prop.unit:
            prop_err_list.append("Unit is not set")
        if prop.unit and not is_si(prop.unit):
            prop_err_list.append("Unit is not valid!")

        if prop_err_list:
            self.errors['sections'][sec_idx]['props'].append(prop_err_list)
            return self.errors
        else:
            return None

    def check_features(self, feat, parent, blk_idx, tag_idx):

        fea_err_list = []

        if not feat.link_type:
            fea_err_list.append("linked type is not set!")
        if not feat.data:
            fea_err_list.append("data is not set")

        if fea_err_list:
            self.errors['blocks'][blk_idx][parent][tag_idx]['fea' \
                                                            'tures'].append(fea_err_list)
            return self.errors
        else:
            return None

    def check_sources(self, src):
        if self.check_for_basics(src):
            pass
        else:
            return None

    def check_dim(self, dimen, da_idx, blk_idx):  # call it in file after the index problem is fixed
        if dimen.index:
            return None
        else:
            self.errors['blocks'][blk_idx]['data_arrays'][da_idx]['di' \
                                                    'mensions'].append('index must > 0')
            return self.errors

    def check_range_dim(self, r_dim, da_idx, blk_idx):
        rdim_err_list = []

        if not r_dim.ticks:
            rdim_err_list.append("ticks need to be set for range dimensions")
        if type(r_dim).__name__ != "RangeDimension" :
            rdim_err_list.append("dimension type is not correct!")

        # sorting is already covered in the dimensions.py file
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


    def check_for_basics(self,entity):
        basic_check_list = []
        a = b = c = ''
        if not entity.type:
            a = "Type of some {} is missing".format(type(entity).__name__)
            basic_check_list.append(a)
        if not entity.id:
            b = "ID of some {} is missing".format(type(entity).__name__)
            basic_check_list.append(b)
        if not entity.name:
            c = "Name of some {} is missing".format(type(entity).__name__)
            basic_check_list.append(c)
        if a == b == c == '':
            return None
        else:
            return basic_check_list








