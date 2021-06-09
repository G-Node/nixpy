#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import nixio
import matplotlib.pyplot as plt


def create_data():
    categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    temperatures = [100, 110, 95, 150, 200, 250]

    return temperatures, categories


def store(nixfile, data, categories):
    b = nixfile.create_block("test", "nix.session")
    data_array = b.create_data_array("category data", "nix.categorical", data=data)
    data_array.label = "temperature"
    data_array.unit = "K"

    data_array.append_set_dimension(categories)

    return data_array


def plot(data_array):
    plt.bar(range(data_array.shape[0]), data_array[:], color="tab:blue")
    plt.xticks(range(data_array.shape[0]), labels=data_array.dimensions[0].labels)
    plt.ylabel("%s %s" % (data_array.label, "[%s]" % data_array.unit if data_array.unit else ""))
    plt.show()


def main():
    data, categories = create_data()

    nixfile = nixio.File.open("categoryData.nix", nixio.FileMode.Overwrite)
    data_array = store(nixfile, data, categories)

    plot(data_array)
    nixfile.close()


if __name__ == "__main__":
    main()
