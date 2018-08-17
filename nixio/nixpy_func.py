from __future__ import (absolute_import, division, print_function)
import nixio as nix

from collections import OrderedDict
import numpy as np
file = nix.File.open('testing.nix', 'a')

x = file.validate()
print(x['blocks'][0]['groups'][0]['grp_err'])

print(x)
file.close()
