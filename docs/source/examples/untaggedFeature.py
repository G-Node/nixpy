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

import lif
import nixio
import numpy as np
import scipy.signal as signal
import matplotlib.pylab as plt


def fake_neuron(stepsize=0.001, offset=.8):
    stimulus = np.random.randn(82000) * 2.5

    b, a = signal.butter(2, 12.5, fs=1 / stepsize, btype="low")
    stimulus = signal.filtfilt(b, a, stimulus[:])
    stimulus = stimulus[1000:-1000]
    s = np.hstack((np.zeros(10000), stimulus, np.zeros(10000)))
    lif_model = lif.LIF(stepsize=stepsize, offset=offset)
    time, v, spike_times = lif_model.run_stimulus(s)

    stimulus_onset = 10000 * stepsize
    stimulus_duration = len(stimulus) * stepsize

    return time, v, stimulus, stimulus_onset, stimulus_duration


def plot_data(tag):
    data_array = tag.references[0]
    voltage = data_array[:]

    x_axis = data_array.dimensions[0]
    time = x_axis.axis(data_array.data_extent[0])

    stimulus_onset = tag.position
    stimulus_duration = tag.extent

    stimulus = tag.feature_data(0)
    stimulus_array = tag.features[0].data

    stim_time_dim = stimulus_array.dimensions[0]
    stimulus_time = stim_time_dim.axis(stimulus_array.data_extent[0])

    response_axis = plt.subplot2grid((2, 2), (0, 0), rowspan=1, colspan=2)
    response_axis.tick_params(direction='out')
    response_axis.spines['top'].set_color('none')
    response_axis.spines['right'].set_color('none')
    response_axis.xaxis.set_ticks_position('bottom')
    response_axis.yaxis.set_ticks_position('left')

    stimulus_axis = plt.subplot2grid((2, 2), (1, 0), rowspan=1, colspan=2)
    stimulus_axis.tick_params(direction='out')
    stimulus_axis.spines['top'].set_color('none')
    stimulus_axis.spines['right'].set_color('none')
    stimulus_axis.xaxis.set_ticks_position('bottom')
    stimulus_axis.yaxis.set_ticks_position('left')

    response_axis.plot(time, voltage, color='tab:blue', label=data_array.name, zorder=1)
    response_axis.set_xlabel(x_axis.label + ((" [" + x_axis.unit + "]") if x_axis.unit else ""))
    response_axis.set_ylabel(data_array.label + ((" [" + data_array.unit + "]") if data_array.unit else ""))
    response_axis.set_xlim(0, np.max(time))
    response_axis.set_ylim((1.2 * np.min(voltage), 1.2 * np.max(voltage)))
    response_axis.barh((np.max(voltage) - np.min(voltage)) / 2, stimulus_duration, np.min(voltage) - np.max(voltage),
                       stimulus_onset, color='silver', alpha=0.5, zorder=0, label="stimulus epoch")
    response_axis.legend(fontsize=9, ncol=2, loc=9)

    stimulus_axis.plot(stimulus_time, stimulus[:], color="slategray", label="stimulus")
    stimulus_axis.set_xlabel(stim_time_dim.label + ((" [" + stim_time_dim.unit + "]") if stim_time_dim.unit else ""))
    stimulus_axis.set_ylabel(stimulus_array.label + ((" [" + stimulus_array.unit + "]") if stimulus_array.unit else ""))
    stimulus_axis.set_xlim(np.min(stimulus_time), np.max(stimulus_time))
    stimulus_axis.set_ylim(1.2 * np.min(stimulus), 1.2 * np.max(stimulus))
    stimulus_axis.legend(fontsize=9, loc=1)

    plt.subplots_adjust(left=0.15, top=0.875, bottom=0.1, right=0.98, hspace=0.45, wspace=0.25)
    plt.gcf().set_size_inches((5.5, 5))
    # plt.savefig("../images/untagged_feature.png")
    plt.show()


if __name__ == '__main__':
    stepsize = 0.0001  # s
    time, voltage, stimulus, stim_onset, stim_duration = fake_neuron(stepsize=stepsize)

    # create a new file overwriting any existing content
    file_name = 'untagged_feature.h5'
    file = nixio.File.open(file_name, nixio.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the membrane voltage
    data = block.create_data_array("membrane voltage", "nix.sampled.time_series", data=voltage,
                                   label="membrane voltage", unit="mV")
    data.append_sampled_dimension(stepsize, label="time", unit="s")

    # create a stimulus DataArray
    stim = block.create_data_array("stimulus", "nix.sampled.time_series", data=stimulus,
                                   label="current stimulus", unit="nA")
    stim.append_sampled_dimension(stepsize, label="time", unit="s")

    # create the Tag to highlight the stimulus-on segment
    tag = block.create_tag("stimulus presentation", "nix.epoch.stimulus_presentation", [stim_onset])
    tag.extent = [stim_duration]
    tag.references.append(data)

    # set stimulus as untagged feature of the tag
    tag.create_feature(stim, nixio.LinkType.Untagged)

    # let's plot the data from the stored information
    plot_data(tag)
    file.close()
