from __future__ import (absolute_import, division, print_function)
import nixio as nix

from collections import OrderedDict
import numpy as np

file = nix.File.open('neoraw.nix', 'a')
print(file.blocks[0].sources)

x = file.validate()
print(x['blocks'][0]['data_arrays'][1]['da_err'])


print(x)
file.close()
