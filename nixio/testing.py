from __future__ import (absolute_import, division, print_function)
import nixio as nix
import h5py
import numpy as np

file = nix.File.open('testing.nix', nix.FileMode.Overwrite)
block = file.create_block("blk1", "blk")
block1 = file.create_block("blk2", "blk")
for blk in block,block1:
    for i in range(2):
        blk.create_group("grp{}".format(i), "groups")
    for i in range(4):
        blk.create_data_array("da{}".format(i), "data_arrays",
                              dtype="float", data=(1+np.random.random((10,10))))
    for i in range(4):
        blk.create_tag("tag{}".format(i), "tags",
                              np.random.random((10,10)))
    for i in range(4):
        blk.create_multi_tag("mt{}".format(i), "multi_tags",
                              blk.data_arrays[i])
block1._h5group.set_attr("name", None)
group1 = block.groups[0]
group1._h5group.set_attr("name", None)
# del block._h5group.group.attrs["name"]
file.close()
