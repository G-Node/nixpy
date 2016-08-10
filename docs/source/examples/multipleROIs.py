#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Copyright © 2014 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

 This tutorial shows how to store image data in nix-files.
 See https://github.com/G-node/nix/wiki for more information.

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
import Image as img
import matplotlib.pyplot as plt


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
    return img_data


def plot_data(tag):
    data_array = tag.references[0]
    img_data = data_array[:]
    img_data = np.array(img_data, dtype='uint8')
    positions_data = tag.positions[:]
    extents_data = tag.extents[:]
    for i in range(positions.data_extent[0]):
        img_data = draw_rect(
            img_data, positions_data[i, :], extents_data[i, :])
    new_img = img.fromarray(img_data)
    new_img.show()


def plot_roi_data(tag):
    position_count = tag.positions.shape[0]
    for p in range(position_count):
        roi_data = tag.retrieve_data(p, 0)[:]
        roi_data = np.array(roi_data, dtype='uint8')
        ax = plt.gcf().add_subplot(position_count, 1, p)
        image = img.fromarray(roi_data)
        ax.imshow(image)
    plt.savefig('retrieved_rois.png')
    plt.show()


if __name__ == '__main__':
    img_data, channels = load_image()
    # create a new file overwriting any existing content
    file_name = 'multiple_roi.h5'
    file = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the sinewave, add some information about
    # the signal
    data = block.create_data_array("lenna", "nix.image.rgb", data=img_data)
    # add descriptors for width, height and channels
    height_dim = data.append_sampled_dimension(1)
    height_dim.label = "height"
    width_dim = data.append_sampled_dimension(1)
    width_dim.label = "width"
    color_dim = data.append_set_dimension()
    color_dim.labels = channels

    # some space for three regions-of-interest
    roi_starts = np.zeros((3, 3))
    roi_starts[0, :] = [250, 245, 0]
    roi_starts[1, :] = [250, 315, 0]
    roi_starts[2, :] = [340, 260, 0]

    roi_extents = np.zeros((3, 3))
    roi_extents[0, :] = [30, 45, 3]
    roi_extents[1, :] = [30, 40, 3]
    roi_extents[2, :] = [25, 65, 3]

    # create the positions DataArray
    positions = block.create_data_array("ROI positions", "nix.positions", data=roi_starts)
    positions.append_set_dimension()  # these can be empty
    positions.append_set_dimension()

    # create the extents DataArray
    extents = block.create_data_array("ROI extents", "nix.extents", data=roi_extents)
    extents.append_set_dimension()
    extents.append_set_dimension()

    # create a MultiTag
    multi_tag = block.create_multi_tag("Regions of interest", "nix.roi", positions)
    multi_tag.extents = extents
    multi_tag.references.append(data)

    # let's plot the data from the stored information
    plot_data(multi_tag)
    plot_roi_data(multi_tag)
    file.close()
