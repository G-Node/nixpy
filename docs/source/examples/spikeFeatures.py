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
import lif
import numpy as np
import scipy.signal as signal
import matplotlib.pylab as plt


def fake_neuron(stepsize=0.001, offset=.8, sta_offset=1000):
    stimulus = np.random.randn(102000) * 3.5
    b, a = signal.butter(1, 12.5, fs=1. / stepsize, btype="low")
    stimulus = signal.filtfilt(b, a, stimulus)
    stimulus = stimulus[1000:-1000]
    lif_model = lif.LIF(stepsize=stepsize, offset=offset)
    time, v, spike_times = lif_model.run_stimulus(stimulus)
    snippets = np.zeros((len(spike_times), 2 * sta_offset))

    for i, t in enumerate(spike_times):
        index = int(round(t / stepsize))
        if index < sta_offset:
            snip = stimulus[0:index + sta_offset]
            snippets[i, -len(snip):] = snip
        elif (index + sta_offset) > len(stimulus):
            snip = stimulus[index - sta_offset:]
            snippets[i, 0:len(snip)] = snip
        else:
            snippets[i, :] = stimulus[index - sta_offset:index + sta_offset]

    return time, v, spike_times, snippets


def plot_data(tag):
    data_array = tag.references[0]
    voltage = np.zeros(data_array.data.shape)
    data_array.data.read_direct(voltage)

    x_axis = data_array.dimensions[0]
    time = x_axis.axis(data_array.data_extent[0])

    spike_times = tag.positions[:]

    feature_data_array = tag.features[0].data
    snippets = tag.features[0].data[:]

    single_snippet = tag.feature_data(3, 0)[:]

    snippet_time_dim = feature_data_array.dimensions[1]
    snippet_time = snippet_time_dim.axis(feature_data_array.data_extent[1])

    response_axis = plt.subplot2grid((2, 2), (0, 0), rowspan=1, colspan=2)
    single_snippet_axis = plt.subplot2grid((2, 2), (1, 0), rowspan=1, colspan=1)
    average_snippet_axis = plt.subplot2grid((2, 2), (1, 1), rowspan=1, colspan=1)

    response_axis.plot(time, voltage, color='dodgerblue', label=data_array.name)
    response_axis.scatter(spike_times, np.ones(spike_times.shape)*np.max(voltage), color='red', label=tag.name)
    response_axis.set_xlabel(x_axis.label + ((" [" + x_axis.unit + "]") if x_axis.unit else ""))
    response_axis.set_ylabel(data_array.label + ((" [" + data_array.unit + "]") if data_array.unit else ""))
    response_axis.set_title(data_array.name)
    response_axis.set_xlim(0, np.max(time))
    response_axis.set_ylim((1.2 * np.min(voltage), 1.2 * np.max(voltage)))
    response_axis.legend(ncol=2, loc="lower center", fontsize=8)

    single_snippet_axis.plot(snippet_time, single_snippet.T, color="red", label=("snippet No 4"))
    single_snippet_axis.set_xlabel(snippet_time_dim.label + ((" [" + snippet_time_dim.unit + "]") if snippet_time_dim.unit else ""))
    single_snippet_axis.set_ylabel(feature_data_array.label + ((" [" + feature_data_array.unit + "]") if feature_data_array.unit else ""))
    single_snippet_axis.set_title("single stimulus snippet")
    single_snippet_axis.set_xlim(np.min(snippet_time), np.max(snippet_time))
    single_snippet_axis.set_ylim((1.2 * np.min(snippets[3,:]), 1.2 * np.max(snippets[3,:])))
    single_snippet_axis.legend()

    mean_snippet = np.mean(snippets, axis=0)
    std_snippet = np.std(snippets, axis=0)
    average_snippet_axis.fill_between(snippet_time, mean_snippet + std_snippet, mean_snippet - std_snippet, color="tab:red", alpha=0.25)
    average_snippet_axis.plot(snippet_time, mean_snippet, color="red", label=(feature_data_array.name + str(4)))
    average_snippet_axis.set_xlabel(snippet_time_dim.label + ((" [" + snippet_time_dim.unit + "]") if snippet_time_dim.unit else ""))
    average_snippet_axis.set_ylabel(feature_data_array.label + ((" [" + feature_data_array.unit + "]") if feature_data_array.unit else ""))
    average_snippet_axis.set_title("spike-triggered average")
    average_snippet_axis.set_xlim(np.min(snippet_time), np.max(snippet_time))
    average_snippet_axis.set_ylim((1.2 * np.min(mean_snippet - std_snippet), 1.2 * np.max(mean_snippet + std_snippet)))

    plt.subplots_adjust(left=0.15, top=0.875, bottom=0.1, right=0.98, hspace=0.35, wspace=0.25)
    plt.gcf().set_size_inches((5.5, 4.5))
    # plt.savefig("../images/spike_features.png")
    plt.show()


def main():
    stepsize = 0.0001  # s
    sta_offset = 1000  # samples
    time, voltage, spike_times, sts = fake_neuron(stepsize=0.0001, sta_offset=sta_offset)

    # create a new file overwriting any existing content
    file_name = 'spike_features.h5'
    file = nixio.File.open(file_name, nixio.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the membrane voltage
    data = block.create_data_array("membrane voltage", "nix.regular_sampled.time_series", data=voltage, label="membrane voltage")
    # add descriptors for the time axis
    data.append_sampled_dimension(stepsize, label="time", unit="s")

    # create the positions DataArray
    positions = block.create_data_array("times", "nix.events.spike_times", data=spike_times)
    positions.append_range_dimension_using_self()

    # create a MultiTag
    multi_tag = block.create_multi_tag("spike times", "nix.events.spike_times", positions)
    multi_tag.references.append(data)

    # save stimulus snippets in a DataArray
    snippets = block.create_data_array("spike triggered stimulus", "nix.regular_sampled.multiple_series", data=sts, label="stimulus", unit="nA")
    snippets.append_set_dimension()
    snippets.append_sampled_dimension(stepsize, offset= -sta_offset * stepsize, label="time", unit="s")

    # set snippets as an indexed feature of the multi_tag
    multi_tag.create_feature(snippets, nixio.LinkType.Indexed)

    # let's plot the data from the stored information
    plot_data(multi_tag)
    file.close()


if __name__ == '__main__':
    main()
