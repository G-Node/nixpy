from __future__ import (absolute_import, division, print_function)
import nixio as nix


file = nix.File.open('neoraw.nix', 'a')


d = file.blocks[0].data_arrays[11].dimensions[0].labels
print(d)
print(len(d))
da = file.blocks[0].data_arrays[11]
print(len(da))
print(da.data_extent)

x = file.validate()
print(x['blocks'][0]['data_arrays'][0]['da_err'])

print(x)
file.close()
