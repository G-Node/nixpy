#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Copyright © 2014 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

 We use the "Lenna" image in this tutorial.

 "Lenna" by Original full portrait: "Playmate of the Month". Playboy
 Magazine. November 1972, photographed by Dwight Hooker.This 512x512
 electronic/mechanical scan of a section of the full portrait:
 Alexander Sawchuk and two others[1] - The USC-SIPI image
 database. Via Wikipedia -
 http://en.wikipedia.org/wiki/File:Lenna.png#mediaviewer/File:Lenna.png

"""

import nixio as nix
import numpy as np
from PIL import Image as img


def load_image():
    image = img.open('lenna.png')
    pix = np.array(image)
    channels = list(image.mode)
    return pix, channels


def draw_rect(img_data, position, extent):
    img_data[position[0]:position[0] + extent[0], position[1], :] = 255
    img_data[position[0]:position[0] + extent[0], position[1] + extent[1], :] = 255
    img_data[position[0], position[1]:position[1] + extent[1], :] = 255
    img_data[position[0] + extent[0], position[1]:position[1] + extent[1], :] = 255


def plot_data(tag):
    data_array = tag.references[0]
    img_data = np.zeros(data_array.data.shape)
    data_array.data.read_direct(img_data)
    img_data = np.array(img_data, dtype='uint8')
    # positions and extents are double by default, need to convert to int
    pos = tuple(map(int, tag.position))
    ext = tuple(map(int, tag.extent))
    draw_rect(img_data, pos, ext)
    new_img = img.fromarray(img_data)

    # new_img.save("../images/single_roi.png")
    new_img.show()


def main():
    img_data, channels = load_image()
    # create a new file overwriting any existing content
    file_name = 'single_roi.nix'
    f = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = f.create_block("block name", "nix.session")

    # create a 'DataArray' to take the sinewave, add some information about the signal
    data = block.create_data_array("lenna", "nix.image.rgb", data=img_data)
    # add descriptors for width, height and channels
    data.append_sampled_dimension(1, label="height")
    data.append_sampled_dimension(1, label="width")
    data.append_set_dimension(labels=channels)

    # create a Tag, position and extent must be 3-D since the data is 3-D
    position = [250, 250, 0]
    extent = [30, 100, 3]
    tag = block.create_tag('Region of interest', 'nix.roi', position)
    tag.extent = extent
    tag.references.append(data)

    # let's plot the data from the stored information
    plot_data(tag)
    f.close()


if __name__ == '__main__':
    main()
