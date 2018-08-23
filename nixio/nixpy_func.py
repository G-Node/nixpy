from __future__ import (absolute_import, division, print_function)
import nixio as nix

from collections import OrderedDict
import numpy as np
file = nix.File.open('testing.nix', 'a')

list_a = [1]
list_b =[0]

for a in list_a:
    if a:
        print("a")
        break

    for b in list_b:
        print("b")


x = file.validate()
print(x['blocks'][0]['data_arrays'][1]['da_err'])

tag = file.blocks[0].tags[0]
print("=====================")
print(tag.units)

print("///////////////////////")
print(x)
file.close()
