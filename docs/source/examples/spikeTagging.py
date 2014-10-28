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

import nix
import lif
import numpy as np
import matplotlib.pylab as plt


def fake_neuron():
    lif_model = lif.lif()
    t, v, spike_times = lif_model.run_const_stim(10000, 0.005)
    return t, v, spike_times

    
def plot_data(tag):
    data_array = tag.references[0]
    voltage = np.zeros(data_array.data.shape)
    data_array.data.read_direct(voltage)
    
    x_axis = data_array.dimensions[0]
    time = np.arange(0, data_array.data.shape[0])
    time = time * x_axis.sampling_interval + (x_axis.offset if x_axis.offset else 0.0)

    spike_times = np.zeros(tag.positions.data_extent)
    tag.positions.data.read_direct(spike_times)

    plt.plot(time, voltage, color='dodgerblue', label=data_array.name)
    plt.scatter(spike_times, np.ones(spike_times.shape)*np.max(voltage), color='red', label=tag.name)
    plt.xlabel(x_axis.label + " [" + x_axis.unit + "]")
    plt.ylabel(data_array.label + " [" + data_array.unit + "]")
    plt.title(data_array.name)
    plt.xlim(0, np.max(time))
    plt.ylim((1.2 * np.min(voltage), 1.2 * np.max(voltage)))
    plt.legend()
    plt.show()


if __name__ == '__main__':
    time, voltage, spike_times = fake_neuron()

    # create a new file overwriting any existing content
    file_name = 'spike_tagging.h5'
    file = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type 
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the membrane voltage
    data = block.create_data_array("membrane voltage", "nix.regular_sampled.time_series", data=voltage)
    data.unit = "V"
    data.label = "voltage"
    # add descriptors for time axis
    time_dim = data.append_sampled_dimension(time[1]-time[0])
    time_dim.label = "time"
    time_dim.unit = "s"
   
    # create the positions DataArray
    positions = block.create_data_array("times", "nix.positions", data=spike_times)
    positions.append_set_dimension() # these can be empty
    positions.append_set_dimension()
    
    # create a MultiTag
    multi_tag = block.create_multi_tag("spike times", "nix.events.spike_times", positions)
    multi_tag.references.append(data)

    # let's plot the data from the stored information
    plot_data(multi_tag)
    file.close()
