from __future__ import (absolute_import, division, print_function)
import nixio as nix

from collections import OrderedDict
import numpy as np
file = nix.File.open('neoraw.nix', 'a')

x = file.validate()
print(x['blocks'][0]['data_arrays'][1]['da_err'])

tag = file.blocks[0].multi_tags[0]
print("=====================")
print(tag.references)
print(tag.id)
print(tag.name)
print(tag.type)
print(tag.definition)
print(len(tag.position))
print(tag.references)
print("///////////////////////")
print(x)
file.close()
