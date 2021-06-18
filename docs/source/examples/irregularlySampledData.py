#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Copyright © 2014-2021 German Neuroinformatics Node (G-Node)

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


def create_data(duration, interval):
    times = np.around(np.cumsum(np.random.poisson(interval * 1000, int(1.5 * duration / interval))) / 1000., 3)
    times = times[times <= duration]
    x = np.arange(0, times[-1] * 2 * np.pi, 0.001)
    y = np.sin(5 * x)
    return times, y[np.asarray(times / 0.001 * 2 * np.pi, dtype=int)]


def plot_data(data_array):
    x_axis = data_array.dimensions[0]
    x = list(x_axis.ticks)
    y = data_array[:]
    plt.plot(x, y, marker='o', color='dodgerblue', label=data_array.name)
    plt.xlabel(x_axis.label + " [" + x_axis.unit + "]")
    plt.ylabel(data_array.label + " [" + data_array.unit + "]")
    plt.legend()
    plt.xlim([0, x[-1]])
    plt.ylim(np.min(y) * 1.1, np.max(y) * 1.1)
    plt.show()


def main():
    # fake some data
    times, values = create_data(1.0, 0.02)

    # create a new file overwriting any existing content
    file_name = 'irregular_data_example.nix'
    file = nixio.File.open(file_name, nixio.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the data, add some information about the signal
    data = block.create_data_array("sinewave", "nix.irregular_sampled", data=values)
    data.unit = "mV"
    data.label = "voltage"
    # add a descriptor for the xaxis
    data.append_range_dimension(ticks=times, label="time", unit="s")

    # let's plot the data from the stored information
    plot_data(data)
    file.close()


if __name__ == "__main__":
    main()
