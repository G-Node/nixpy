#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Copyright © 2014 - 2021 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

 See https://github.com/G-node/nix/wiki for more information.
"""

import nixio
import numpy as np
import matplotlib.pyplot as plt


def create_sinewave(duration=1, freq=10, stepsize=0.01):
    x = np.arange(0, duration * 2 * np.pi, stepsize)
    y = np.sin(freq * x)
    return x, y


def plot_data(data_array):
    x_axis = data_array.dimensions[0]
    x = x_axis.axis(data_array.data.shape[0])
    y = data_array.data[:]

    plt.plot(x, y, marker=".", markersize=5, label=data_array.name)
    plt.xlabel(x_axis.label + " [" + x_axis.unit + "]")
    plt.ylabel(data_array.label + " [" + data_array.unit + "]")
    plt.xlim(0, np.max(x))
    plt.ylim((1.1 * np.min(y), 1.1 * np.max(y)))
    plt.legend()
    plt.show()


def main():
    # fake some data
    duration = 10.
    frequency = 5
    stepsize = 0.002
    _, y = create_sinewave(duration, frequency, stepsize)

    # create a new file overwriting any existing content
    file_name = 'regular_data_example.nix'
    file = nixio.File.open(file_name, nixio.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the sinewave, add some information about the signal
    data = block.create_data_array("sinewave", "nix.regular_sampled", data=y)
    data.unit = "mV"
    data.label = "voltage"
    # add a descriptor for the xaxis
    data.append_sampled_dimension(stepsize, label="time", unit="s", offset=0.0)

    # let's plot the data from the stored information
    plot_data(data)
    file.close()


if __name__ == "__main__":
    main()
