#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Copyright © 2014 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

 See https://github.com/G-node/nix/wiki for more information.

"""

import nixio as nix
import numpy as np
import matplotlib.pylab as plt


def create_data(duration=1, freq=10, stepsize=0.01):
    x = np.arange(0, duration * 2 * np.pi, stepsize)
    sine = np.sin(freq * x)
    cosine = np.cos(freq * x)
    return x, sine, cosine


def plot_data(data_array):
    set_dim = data_array.dimensions[0]
    x_axis = data_array.dimensions[1]
    x = np.arange(0, data_array.shape[1])
    x = x * x_axis.sampling_interval + x_axis.offset
    y = np.zeros(data_array.shape)
    data_array.read_direct(y)
    for i, label in enumerate(set_dim.labels):
        plt.plot(x, y[i, :], label=label)

    plt.xlabel(x_axis.label + " [" + x_axis.unit + "]")
    plt.ylabel(data_array.label + " [" + data_array.unit + "]")
    plt.title(data_array.name)
    plt.xlim(0, np.max(x))
    plt.ylim((1.1 * np.min(y), 1.1 * np.max(y)))
    plt.legend()
    plt.savefig('multiple_time_series.png')
    plt.show()

def main():
    # fake some data
    duration = 2
    frequency = 2
    stepsize = 0.02
    _, sine, cosine = create_data(duration, frequency, stepsize)

    # create a new file overwriting any existing content
    file_name = 'multiple_regular_data_example.h5'
    file = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = file.create_block("block name", "nix.session")
    # create a 'DataArray' to take the data, add some information about the signal
    y = np.vstack((sine, cosine))
    data = block.create_data_array("waveforms", "nix.regular_sampled.multiple_series", data=y, label="voltage", unit="mV")
    # descriptor for first dimension is a set
    data.append_set_dimension(labels=['sin', 'cos'])
    # add a descriptor for the xaxis
    data.append_sampled_dimension(stepsize, offset=0.0, label="time", unit="s")

    # let's plot the data from the stored information
    plot_data(data)
    file.close()


if __name__ == "__main__":
    main()
