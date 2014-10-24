#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nix
import numpy as np
import matplotlib.pylab as plt


def create_sinewave(duration=1, freq=10, stepsize=0.01):
    x = np.arange(0, duration*2*np.pi, stepsize)
    y = np.sin(freq*x)
    return x, y 


def plot_data(data_array):
    x_axis = data_array.dimensions[0]
    x = np.arange(0, data_array.data.shape[0])
    x = x * x_axis.sampling_interval + x_axis.offset
    y = data_array.data
    plt.plot(x, y)
    plt.xlabel(x_axis.label + " [" + x_axis.unit + "]")
    plt.ylabel(data_array.label + " [" + data_array.unit + "]")
    plt.title(data_array.name)
    plt.xlim(0, np.max(x))
    plt.ylim((1.1 * np.min(y), 1.1 * np.max(y)))
    plt.show()


if __name__ == "__main__":
    # fake some data
    duration = 2
    frequency = 20
    stepsize = 0.02
    x, y = create_sinewave(duration, frequency, stepsize)
    
    # create a new file overwriting any existing content
    file_name = 'regular_data_example.h5'
    file = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type 
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the sinewave, add some information about the signal
    data = block.create_data_array("sinewave", "nix.regular_sampled", data=y)
    data.unit = "mV"
    data.label = "voltage"
    # add a descriptor for the xaxis
    dim = data.append_sampled_dimension(stepsize)
    dim.unit = "s"
    dim.label = "time"
    dim.offset = 0.0 # optional
    
    # let's plot the data from the stored information
    plot_data(data)
    file.close()
