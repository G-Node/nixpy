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
        assert self.created_at, "date is not set!"
        assert self.format, "format is not set!"
        assert self.version, "version is not set!"
        # in nixpy no location attributes. This is checked in C++ version

    def check_blocks(self):
        for blk in self.blocks:
            assert blk.name, "blocks should have name"
            assert blk.type, 'blocks should have type'

    def check_data_array(self):
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
        pass

    def check_multi_tag(self):
        pass

    def check_section(self):
        pass

    def check_for_basics(idx, entity):
        a = b = c = ''
        if not entity.type:
            a = "Type of {} {} is missing".format(entity, idx)
        if not entity.id:
            b = "ID of {} {} is missing".format(entity, idx)
        if not entity.name:
            c = "Name of {} {} is missing".format(entity, idx)
        return a,b,c






