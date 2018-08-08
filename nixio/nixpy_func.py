from __future__ import (absolute_import, division, print_function)
import nixio as nix


file = nix.File.open('testing.nix', 'a')





x = file.validate()
print(x['blocks'][0]['data_arrays'][0]['dimensions'])

print(x)
file.close()
