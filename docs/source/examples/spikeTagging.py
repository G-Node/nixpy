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
import matplotlib.pylab as plt


def fake_neuron():
    lif_model = lif.LIF(offset=1.0)
    t, v, spike_times = lif_model.run_const_stim(5000, 0.00025)
    return t, v, spike_times


def plot_data(tag):
    data_array = tag.references[0]
    voltage = np.zeros(data_array.data.shape)
    data_array.data.read_direct(voltage)

    x_axis = data_array.dimensions[0]
    time = x_axis.axis(data_array.data.shape[0])

    spike_times = np.zeros(tag.positions.data_extent)
    tag.positions.data.read_direct(spike_times)

    fig = plt.figure(figsize=(5.5, 2.5))
    ax = fig.add_subplot(111)
    ax.plot(time, voltage, color='dodgerblue', label=data_array.name)
    ax.scatter(spike_times, np.ones(spike_times.shape)*np.max(voltage), color='red', label=tag.name)
    ax.set_xlabel(x_axis.label + ((" [" + x_axis.unit + "]") if x_axis.unit else ""))
    ax.set_ylabel(data_array.label + ((" [" + data_array.unit + "]") if data_array.unit else ""))
    ax.set_xlim(0, np.max(time))
    ax.set_ylim((1.5 * np.min(voltage), 1.5 * np.max(voltage)))
    ax.legend()
    fig.subplots_adjust(bottom=0.175, top=0.975, right=0.975)
    fig.savefig("../images/spike_tagging.png")
    plt.show()


if __name__ == '__main__':
    time, voltage, spike_times = fake_neuron()

    # create a new file overwriting any existing content
    file_name = 'spike_tagging.nix'
    file = nixio.File.open(file_name, nixio.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the membrane voltage
    data = block.create_data_array("membrane voltage", "nix.regular_sampled.time_series", data=voltage, label="membrane voltage", unit="mV")

    # add descriptors for time axis
    data.append_sampled_dimension(time[1]-time[0], label="time", unit="s")

    # create the positions DataArray
    positions = block.create_data_array("spike times", "nix.events.spike_times", data=spike_times)
    positions.append_range_dimension_using_self()

    # create a MultiTag
    multi_tag = block.create_multi_tag("spike times", "nix.events.spike_times", positions)
    multi_tag.references.append(data)

    # let's plot the data from the stored information
    plot_data(multi_tag)
    file.close()
