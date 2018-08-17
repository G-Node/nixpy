from __future__ import (absolute_import, division, print_function)
import nixio as nix

from collections import OrderedDict
import numpy as np
file = nix.File.open('testing.nix', 'a')
da3 = file.blocks[1].data_arrays[0]
da3.data_extent = (10, )
print(da3.data_extent)
print(da3[:])
x = file.validate()
print(x['blocks'][0]['data_arrays'][1]['da_err'])


print(x['blocks'][1]['data_arrays'][0]['da_err'] )
da= file.blocks[0].data_arrays[1]

# print(da.dimensions)
# print(len(da))
# print(da.data_extent)
# print(len(da.dimensions[0].labels))
print(x)
file.close()
