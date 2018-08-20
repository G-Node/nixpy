from __future__ import (absolute_import, division, print_function)
import nixio as nix

from collections import OrderedDict
import numpy as np
file = nix.File.open('testing.nix', 'a')

a = 1

assert a == 0 or 1

x = file.validate()
print(x['blocks'][0]['data_arrays'][1]['da_err'])

tag = file.blocks[0].tags[0]
print("=====================")
print(tag.units)

print("///////////////////////")
print(x)
file.close()
