#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Copyright © 2014 - 2021 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

 See https://github.com/G-node/nix/wiki for more information.

 We use the "Lenna" image in this tutorial.

 "Lenna" by Original full portrait: "Playmate of the Month". Playboy
 Magazine. November 1972, photographed by Dwight Hooker.This 512x512
 electronic/mechanical scan of a section of the full portrait:
 Alexander Sawchuk and two others[1] - The USC-SIPI image
 database. Via Wikipedia -
 http://en.wikipedia.org/wiki/File:Lenna.png#mediaviewer/File:Lenna.png

"""

import nixio
import numpy as np
from PIL import Image as img

import docutils


def load_image():
    image = img.open('boats.png')
    pix = np.array(image)
    channels = list(image.mode)
    return pix, channels


def plot_data(data_array):
    img_data = np.zeros(data_array.shape)
    data_array.read_direct(img_data)
    img_data = np.array(img_data, dtype='uint8')
    new_img = img.fromarray(img_data)
    if not docutils.is_running_under_pytest():
        new_img.show()


if __name__ == '__main__':
    img_data, channels = load_image()
    # create a new file overwriting any existing content
    file_name = 'image_example.nix'
    file = nixio.File.open(file_name, nixio.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' and store the image data
    data = block.create_data_array("lenna", "nix.image.rgb", data=img_data)
    # add descriptors for width, height and channel dimensions
    data.append_sampled_dimension(1, label="height")
    data.append_sampled_dimension(1, label="width")
    data.append_set_dimension(labels=channels)

    # let's plot the data from the stored information
    plot_data(data)
    file.close()
