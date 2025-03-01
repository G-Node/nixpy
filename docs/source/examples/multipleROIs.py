#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Copyright © 2014 - 2021 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

 See https://github.com/G-node/nix/wiki for more information.

"""

import nixio
import numpy as np
from PIL import Image as img
import matplotlib.pyplot as plt

import docutils


def load_image():
    image = img.open('boats.png')
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
    positions = tag.positions
    img_data = data_array[:]
    img_data = np.array(img_data, dtype='uint8')
    positions_data = tag.positions[:]
    extents_data = tag.extents[:]
    for i in range(positions.data_extent[0]):
        img_data = draw_rect(img_data, positions_data[i, :], extents_data[i, :])
    # new_img = img.fromarray(img_data)
    plt.imshow(img_data)
    plt.gcf().set_size_inches((5.5, 5.5))
    if docutils.is_running_under_pytest():
        plt.close()
    else:
        plt.savefig("../images/multiple_rois.png")
        plt.show()


def plot_roi_data(tag):
    position_count = tag.positions.shape[0]

    fig = plt.figure(figsize=(5.5, 5.5))
    for p in range(position_count):
        roi_data = tag.tagged_data(p, "boats")[:]
        roi_data = np.array(roi_data, dtype='uint8')
        ax = fig.add_subplot(position_count, 1, p + 1)
        image = img.fromarray(roi_data)
        ax.imshow(image)

    if docutils.is_running_under_pytest():
        plt.close()
    else:
        fig.savefig('../images/retrieved_rois.png')
        plt.show()


def main():
    img_data, channels = load_image()
    # create a new file overwriting any existing content
    file_name = 'multiple_roi.nix'
    file = nixio.File.open(file_name, nixio.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the sinewave, add some information about
    # the signal
    data = block.create_data_array("boats", "nix.image.rgb", data=img_data)
    # add descriptors for width, height and channels
    data.append_sampled_dimension(1, label="height")
    data.append_sampled_dimension(1, label="width")
    data.append_set_dimension(labels=channels)

    num_regions = 3
    num_dimensions = len(data.dimensions)
    roi_starts = np.zeros((num_regions, num_dimensions), dtype=int)
    roi_starts[0, :] = [170, 50, 0]
    roi_starts[1, :] = [250, 310, 0]
    roi_starts[2, :] = [120, 425, 0]

    roi_extents = np.zeros((num_regions, num_dimensions), dtype=int)
    roi_extents[0, :] = [240, 175, 3]
    roi_extents[1, :] = [60, 135, 3]
    roi_extents[2, :] = [170, 125, 3]

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


if __name__ == '__main__':
    main()
