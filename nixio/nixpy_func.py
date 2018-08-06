from __future__ import (absolute_import, division, print_function)
import nixio as nix

file = nix.File.open('neoraw.nix', 'a')

x = file.validate()
print(x)

file.close()
