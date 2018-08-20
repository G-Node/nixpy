from __future__ import (absolute_import, division, print_function)
import nixio as nix
import h5py
import numpy as np

file = nix.File.open('testing.nix', nix.FileMode.Overwrite)

block = file.create_block("blk1", "blk")
block1 = file.create_block("blk2", "blk")
for blk in block,block1:
   # blk.create_section("metadata", "md")  # create metatdata
    for i in range(2):
        blk.create_group("grp{}".format(i), "groups")
    for i in range(4):
        blk.create_data_array("da{}".format(i), "data_arrays abc",
                              dtype="float", data=(1+np.random.random((5))))
    for i in range(4):
        blk.create_tag("tag{}".format(i), "tag",
                              np.random.random(10))
    for i in range(4):
        blk.create_multi_tag("mt{}".format(i), "multi_tags",
                              blk.data_arrays[i])

# deleting attributes to create errors
block1._h5group.set_attr("name", None)
group1 = block.groups[0]
group1._h5group.set_attr("name", None)




da1 = block.data_arrays[0]
da1.append_range_dimension([1, 2, 3, 4, 5,6,7,8,9])
da1.append_sampled_dimension( 0.5)
da1.append_set_dimension()  # correct set dimension
da1._h5group.set_attr("unit", "abcde")
da1._h5group.set_attr("expansion_origin" ,  [0.11, 0.22])

tag1 = block.tags[0]
tag1.references.append(da1)

da2 = block.data_arrays[1]
da2.append_set_dimension()
da2.dimensions[0]._h5group.set_attr("labels", None)

# del block._h5group.group.attrs["name"]
file.close()
