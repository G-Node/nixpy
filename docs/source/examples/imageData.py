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


def load_image():
    image = img.open('lenna.png')
    pix = np.array(image)
    channels = list(image.mode)
    return pix, channels


def plot_data(data_array):
    img_data = np.zeros(data_array.data.shape)
    data_array.data.read_direct(img_data)
    img_data = np.array(img_data, dtype='uint8')
    new_img = img.fromarray(img_data)
    new_img.show()
        

if __name__ == '__main__':
    img_data, channels = load_image()
    # create a new file overwriting any existing content
    file_name = 'image_example.h5'
    file = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type 
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the sinewave, add some information about the signal
    data = block.create_data_array("lenna", "nix.image.rgb", data=img_data)
    # add descriptors for width, height and channels
    height_dim = data.append_sampled_dimension(1)
    height_dim.label = "height"
    width_dim = data.append_sampled_dimension(1)
    width_dim.label = "width"
    color_dim = data.append_set_dimension()
    color_dim.labels = channels
    
    # let's plot the data from the stored information
    plot_data(data)
    file.close()
