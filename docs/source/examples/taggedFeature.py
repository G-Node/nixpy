#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Copyright © 2014 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

 See https://github.com/G-node/nix/wiki for more information.

"""
import nixio
import lif
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt


def fake_neuron(stepsize=0.001, offset=.8):
    stimulus = np.random.randn(102000) * 2.5
    b, a = signal.butter(2, 7.5, fs=1. / stepsize, btype="low")
    stimulus = signal.filtfilt(b, a, stimulus)
    stimulus = stimulus[1000:-1000]

    lif_model = lif.LIF(stepsize=stepsize, offset=offset)
    time, v, spike_times = lif_model.run_stimulus(stimulus)
    return time, v, stimulus, spike_times


def main():
    stepsize = 0.0001 # s
    time, voltage, stimulus, spike_times = fake_neuron(stepsize=0.0001)

    # create a new file overwriting any existing content
    file_name = 'spike_features.nix'
    file = nixio.File.open(file_name, nixio.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the membrane voltage
    data = block.create_data_array("membrane voltage", "nix.regular_sampled.time_series", data=voltage)
    data.label = "membrane voltage"
    data.unit = "mV"
    # add descriptors for the time axis
    data.append_sampled_dimension(stepsize, label="time", unit="s")

    # create the positions DataArray
    positions = block.create_data_array("spike times", "nix.events.spike_times", data=spike_times)
    positions.append_range_dimension_using_self()

    # create a MultiTag
    multi_tag = block.create_multi_tag("spike times", "nix.events.spike_times", positions)
    multi_tag.references.append(data)

    # save stimulus snippets in a DataArray
    stimulus_array = block.create_data_array("stimulus", "nix.sampled", data=stimulus, label="stimulus", unit="nA")
    # add a descriptor for the time axis
    stimulus_array.append_sampled_dimension(stepsize, label="time", unit="s")

    # set stimulus as a tagged feature of the multi_tag
    multi_tag.create_feature(stimulus_array, nixio.LinkType.Tagged)

    # let's plot the data from the stored information
    plot_data(multi_tag)
    file.close()


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

    stim_at_spike_time = np.zeros(len(tag.positions[:]))

    for i in range(len(tag.positions)):
        stim_at_spike_time[i] = tag.feature_data(i, 0)[:]

    response_axis = plt.subplot2grid((2, 3), (0, 0), rowspan=1, colspan=2)
    stimulus_axis = plt.subplot2grid((2, 3), (1, 0), rowspan=1, colspan=2, sharex=response_axis)

    hist_axis = plt.subplot2grid((2, 3), (1, 2), rowspan=1, colspan=1)
    hist_axis.hist([stimulus, stim_at_spike_time], color=["tab:blue", "orange"], label=["stimulus", "spike triggered stim"], density=True)
    hist_axis.set_xlabel("%s [%s]" % (feature_data_array.label, feature_data_array.unit))
    hist_axis.set_ylabel("probability density")
    hist_axis.legend(ncol=1, fontsize=8, loc=(-0.1, 1.025))

    response_axis.plot(time, voltage, color='tab:blue', label=data_array.name, lw=1)
    response_axis.scatter(spike_times, np.ones(spike_times.shape) * np.max(voltage), color='red', label=tag.name)
    response_axis.set_ylabel(data_array.label + ((" [" + data_array.unit + "]") if data_array.unit else ""))
    response_axis.set_xlim(0, np.max(time))
    response_axis.set_ylim((1.2 * np.min(voltage), 1.2 * np.max(voltage)))
    response_axis.legend(loc="lower center", ncol=2, fontsize=8)

    stimulus_axis.plot(stimulus_time, stimulus, color="darkgray", label="stimulus", lw=1)
    stimulus_axis.scatter(spike_times, np.ones(spike_times.shape)*np.max(stimulus), color='red', label=tag.name)
    stimulus_axis.set_xlabel(stim_time_dim.label + ((" [" + stim_time_dim.unit + "]") if stim_time_dim.unit else ""))
    stimulus_axis.set_ylabel(feature_data_array.label + ((" [" + feature_data_array.unit + "]") if feature_data_array.unit else ""))
    stimulus_axis.set_xlim(np.min(stimulus_time), np.max(stimulus_time))
    stimulus_axis.set_ylim(1.2 * np.min(stimulus), 1.2 * np.max(stimulus))
    stimulus_axis.legend(loc="lower center", ncol=2, fontsize=8)

    plt.subplots_adjust(left=0.125, top=0.975, bottom=0.1, right=0.98, hspace=0.25, wspace=0.35)
    plt.gcf().set_size_inches((5.5, 4.5))
    # plt.savefig('../images/tagged_feature.png')
    plt.show()

if __name__ == '__main__':
    main()

