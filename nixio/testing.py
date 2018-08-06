from __future__ import (absolute_import, division, print_function)
import nixio as nix
import h5py

file = h5py.File('neoraw.nix', 'a')
print(file)
file.close()
