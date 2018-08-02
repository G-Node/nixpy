from __future__ import (absolute_import, division, print_function)
import os
import shutil
import unittest
import h5py
import numpy as np
import nixio as nix

class Validate():

    def __init__(self, file=''):
        self.file = nix.File.open(file)


    def check_blocks(self):
        pass

    def check_data_array(self):
        valid_check_list = []
        for blk in self.file.blocks:
            for da in blk.data_arrays:
                if da == None:
                    valid_check_list.append(False)
                    return valid_check_list
        valid_check_list.append(True)

        for blk in self.file.blocks:
            for da in blk.data_arrays:
                for dim in da.dimensions:
                    dim_len = len(dim)
                    len_dim = da.data_extent
                    if dim_len == len_dim
                        continue
                    valid_check_list.append(False)
                    break
        valid_check_list.append(True)

        




