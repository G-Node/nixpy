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

            # valid_blk = self.check_for_basics(bi, blk)
            # if valid_blk:
            #     self.errors['blocks'].append(valid_blk)

            for gi, da in enumerate(blk.data_arrays):
                d = {'dimensions': []}
                self.errors['blocks'][bi]['data_arrays'].append(d)

                # seg_list = self.errors['blocks'][bi]['groups'][gi]

                # valid_grp = self.check_for_basics(gi, grp)
                # if valid_grp:
                #     seg_list.append(valid_grp)
                #
                # for di, da in enumerate(blk.data_arrays):
                #     valid_da = self.check_for_basics(di, da)
                #     if valid_da:
                #         seg_list['data_arrays'][di].append(valid_da)
                #
                # for ti, tags in enumerate(grp.tags):
                #     valid_tag = self.check_for_basics(ti, tags)
                #     if valid_tag:
                #         seg_list['tags'][ti].append(valid_tag)
                #
                # for mti, multag in enumerate(grp.multi_tags):
                #     valid_multag = self.check_for_basics(mti, multag)
                #     if valid_multag:
                #         seg_list['multi_tags'][mti].append(valid_multag)

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


        # for blk in self.file.blocks:
        #     for da in blk.data_arrays:
        #         if da == []:
        #             valid_check_list.append(False)
        #
        # valid_check_list.append(True)
        #
        # for blk in self.file.blocks:
        #     for i, da in enumerate(blk.data_arrays):
        #         dim = da.shape
        #         len_dim = da.data_extent  # not sure if this make sense
        #         if dim == len_dim:
        #             continue
        #         valid_check_list.append(False)
        #         break
        # valid_check_list.append(True)
        #
        # for blk in self.file.blocks:
        #     for da in blk.data_arrays:
        #         unit = da.unit
        #         if is_si(unit):
        #             continue
        #         valid_check_list.append(False)
        # valid_check_list.append(True)
        #
        # for blk in self.file.blocks:
        #     for da in blk.data_arrays:
        #         poly = da.polynom_coefficients
        #         ex_origin = da.expansion_origin
        #         if ex_origin:
        #             assert poly, "Expansion origins exist but " \
        #                          "polynomial coefficients are missing!"
        #         if poly:
        #             assert ex_origin, "Polynomial coefficients exist" \
        #                               " but expansion origins are missing"
        #
        # valid_check_list = np.array(valid_check_list)
        # assert np.all(valid_check_list) == True, "Some/all data_arrays are invalid"

    def check_tag(self, tag):
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
                if prop.unit and is_si(prop.unit) == False:
                    a = "The unit is not valid!"

    def check_features(self):
        pass

    def check_sources(self):
        self.check_for_basics()

    def check_dim(self):
        pass

    def check_range_dim(self):
        pass

    def check_set_dim(self):
        pass

    def check_sampled_dim(self):
        pass

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








