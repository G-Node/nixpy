#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Copyright © 2014 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

 This tutorial shows how to store a voltage trace, mark in this the
 occurence of action poentials, and save the stimulus as a feature.

 See https://github.com/G-node/nix/wiki for more information.

"""

import nixio as nix
import lif
import numpy as np
import scipy.signal as signal
import matplotlib.pylab as plt


def fake_neuron(stepsize=0.001, offset=.8):
    stimulus = np.random.randn(100000) * 2.5
    b, a = signal.butter(8, 0.125)
    stimulus = signal.filtfilt(b, a, stimulus)
    lif_model = lif.lif(stepsize=stepsize, offset=offset)
    time, v, spike_times = lif_model.run_stimulus(stimulus)
    return time, v, stimulus, spike_times


def plot_data(tag):
    data_array = tag.references[0]
    voltage = data_array[:]

    x_axis = data_array.dimensions[0]
    time = x_axis.axis(data_array.data_extent[0])

    spike_times = tag.positions[:]

    feature_data_array = tag.features[0].data
    stimulus = feature_data_array[:]

    stim_time_dim = feature_data_array.dimensions[0]
    stimulus_time = stim_time_dim.axis(feature_data_array.data_extent[0])

    response_axis = plt.subplot2grid((2, 2), (0, 0), rowspan=1, colspan=2)
    stimulus_axis = plt.subplot2grid((2, 2), (1, 0), rowspan=1, colspan=2, sharex=response_axis)

    response_axis.plot(time, voltage, color='dodgerblue', label=data_array.name)
    response_axis.scatter(spike_times, np.ones(spike_times.shape)*np.max(voltage), color='red', label=tag.name)
    response_axis.set_xlabel(x_axis.label + ((" [" + x_axis.unit + "]") if x_axis.unit else ""))
    response_axis.set_ylabel(data_array.label + ((" [" + data_array.unit + "]") if data_array.unit else ""))
    response_axis.set_title(data_array.name)
    response_axis.set_xlim(0, np.max(time))
    response_axis.set_ylim((1.2 * np.min(voltage), 1.2 * np.max(voltage)))
    response_axis.legend()

    stimulus_axis.plot(stimulus_time, stimulus, color="black", label="stimulus")
    stimulus_axis.scatter(spike_times, np.ones(spike_times.shape)*np.max(stimulus), color='red', label=tag.name)
    stimulus_axis.set_xlabel(stim_time_dim.label + ((" [" + stim_time_dim.unit + "]") if stim_time_dim.unit else ""))
    stimulus_axis.set_ylabel(feature_data_array.label + ((" [" + feature_data_array.unit + "]") if feature_data_array.unit else ""))
    stimulus_axis.set_title("stimulus")
    stimulus_axis.set_xlim(np.min(stimulus_time), np.max(stimulus_time))
    stimulus_axis.set_ylim(1.2 * np.min(stimulus), 1.2 * np.max(stimulus))
    stimulus_axis.legend()

    plt.subplots_adjust(left=0.15, top=0.875, bottom=0.1, right=0.98, hspace=0.45, wspace=0.25)
    # plt.savefig('taggedFeature.png')
    plt.show()


if __name__ == '__main__':
    stepsize = 0.0001 # s
    time, voltage, stimulus, spike_times = fake_neuron(stepsize=0.0001)

    # create a new file overwriting any existing content
    file_name = 'spike_features.h5'
    file = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the membrane voltage
    data = block.create_data_array("membrane voltage", "nix.regular_sampled.time_series", data=voltage)
    data.label = "membrane voltage"
    # add descriptors for the time axis
    time_dim = data.append_sampled_dimension(stepsize)
    time_dim.label = "time"
    time_dim.unit = "s"

    # create the positions DataArray
    positions = block.create_data_array("times", "nix.positions", data=spike_times)
    positions.append_set_dimension() # these can be empty
    positions.append_set_dimension()

    # create a MultiTag
    multi_tag = block.create_multi_tag("spike times", "nix.events.spike_times", positions)
    multi_tag.references.append(data)

    # save stimulus snippets in a DataArray
    stimulus_array = block.create_data_array("stimulus", "nix.regular_sampled", data=stimulus)
    stimulus_array.label = "stimulus"
    stimulus_array.unit = "nA"
    # add a descriptor for the time axis
    dim = stimulus_array.append_sampled_dimension(stepsize)
    dim.unit = "s"
    dim.label = "time"

    # set stimulus as a tagged feature of the multi_tag
    multi_tag.create_feature(stimulus_array, nix.LinkType.Tagged)

    # let's plot the data from the stored information
    plot_data(multi_tag)
    file.close()
