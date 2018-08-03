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
        pass

    def check_blocks(self):
        pass

    def check_data_array(self):
        valid_check_list = []

        for blk in self.blocks:
            for da in blk.data_arrays:
                if da == None:
                    valid_check_list.append(False)
        valid_check_list.append(True)

        for blk in self.blocks:
            for i, da in enumerate(blk.data_arrays):
                print( da.type, da.dimensions)
                print("Sig{} is {}".format(i,da.data_extent))
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

        valid_check_list = np.array(valid_check_list)
        assert np.all(valid_check_list) == True , "Some/all data_arrays are invalid"

    def check_tag(self):
        pass

    def check_multi_tag(self):
        pass

    def check_section(self):
        pass






