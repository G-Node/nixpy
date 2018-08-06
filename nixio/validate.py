from __future__ import (absolute_import, division, print_function)
import os
import shutil
import unittest
import h5py
import numpy as np
import quantities as pq
import nixio as nix
from .exceptions import *
from .util.units import *

class Validate():



    def __init__(self, file=''):
        self.file = nix.File.open(file)

    def check_file(self):

        if not self.created_at: print("date is not set!")
        if not self.format: print("format is not set!")
        if not self.version: print("version is not set!")
        # in nixpy no location attributes. This is checked in C++ version

    def check_blocks(self):
        blk_dict = {}

        for blk in self.blocks:
            assert blk.name, "blocks should have name"
            assert blk.type, 'blocks should have type'

    def check_data_array(self):  # maybe I should seperate the checks of da and dims
        valid_check_list = []


        for blk in self.blocks:
            for da in blk.data_arrays:
                if da == []:
                    valid_check_list.append(False)

        valid_check_list.append(True)

        for blk in self.blocks:
            for i, da in enumerate(blk.data_arrays):
                dim = da.shape
                len_dim = da.data_extent  # not sure if this make sense
                if dim == len_dim:
                    continue
                valid_check_list.append(False)
                break
        valid_check_list.append(True)

        for blk in self.blocks:
            for da in blk.data_arrays:
                unit = da.unit
                if is_si(unit):
                    continue
                valid_check_list.append(False)
        valid_check_list.append(True)

        for blk in self.blocks:
            for da in blk.data_arrays:
                poly = da.polynom_coefficients
                ex_origin = da.expansion_origin
                if ex_origin:
                    assert poly, "Expansion origins exist but " \
                                 "polynomial coefficients are missing!"
                if poly:
                    assert ex_origin, "Polynomial coefficients exist" \
                                      " but expansion origins are missing"

        valid_check_list = np.array(valid_check_list)
        assert np.all(valid_check_list) == True, "Some/all data_arrays are invalid"

    def check_tag(self):
        for blk in self.blocks:
            for grp in blk.groups:
                for tag in grp.tags:
                    if not tag.position:
                        a = "Position is not set!"
                    if tag.references:  # referenced da dimension and units should match the tag
                        pass
                    if tag.units:
                        if not is_si(tag.units):
                            b = "It is not a valid unit"
                        if tag.references.units != tag.units:
                            c = "Some of the referenced DataArrays' dimensions don't " \
                                "have units where the tag has. Make sure that all referen" \
                                "ces have the same number of dimensions as the tag has un" \
                                "its and that each dimension has a unit set."


    def check_multi_tag(self):
        for blk in self.blocks:
            for grp in blk.groups:
                for mt in grp.multi_tags:
                    if not mt.positions:
                        a = "Position is not set!"
                    if mt.references:
                        pass
                    if mt.units:
                        if not is_si(mt.units):
                            b = "It is not a valid unit"
                        if mt.references.units != mt.units:
                            pass

    def check_section(self):
        for meta in self.metadata:  # this part may be replaced by check_for_basics
            if not meta.name:
                pass
            if not meta.id:
                pass
            if not meta.type:
                pass
            for prop in meta.property:
                if not prop.unit:
                    b = "Why there is no unit?"
                    continue
                if is_si(prop.unit):
                    a = "The unit is not valid!"


    def check_for_basics(idx, entity):
        a = b = c = ''
        print(entity.type)
        if not entity.type:
            a = "Type of {} {} is missing".format(entity, idx)
        if not entity.id:
            b = "ID of {} {} is missing".format(entity, idx)
        if not entity.name:
            c = "Name of {} {} is missing".format(entity, idx)
        if a or b or c:
            return a,b,c
        else:
            pass






