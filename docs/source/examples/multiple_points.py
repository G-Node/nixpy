import nixio
import numpy as np
import matplotlib.pyplot as plt


def create_data(interval=0.001):
    time = np.arange(0., 1.0, interval)
    freq = 5.
    signal = np.sin(time * 2 * np.pi * freq) + np.sin(time * 2 * np.pi * 2 * freq) * 0.4
    events = time[(signal > 0.5) & (np.roll(signal, -1) <= 0.5)]
    return signal, events


def plot(multi_tag):
    event_array = multi_tag.positions
    event_times = multi_tag.positions[:]
    signal_array = multi_tag.references["signal"]
    signal = signal_array[:]
    x_axis = signal_array.dimensions[0]
    time = x_axis.axis(len(signal))

    fig = plt.figure()
    fig.set_size_inches(5.5, 2.5)
    ax = fig.add_subplot(111)
    ax.plot(time, signal, label='voltage', zorder=0)
    ax.scatter(event_times, np.ones(event_times.shape) * 0.5, marker=".", s=75, color='red',
               label=event_array.name, zorder=1)

    ax.set_xlim([0., 1.])
    ax.set_ylim([-1.75, 1.75])
    ax.set_xticks(np.arange(0, 1.01, 0.25))
    ax.set_yticks(np.arange(-1.5, 1.6, 0.5))
    ax.set_xlabel(x_axis.label + ((" [" + x_axis.unit + "]") if x_axis.unit else ""))
    ax.set_ylabel("%s [%s]" % (signal_array.label, signal_array.unit))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.subplots_adjust(bottom=0.175, left=0.15, right=0.95, top=0.95)
    ax.legend(loc=3, frameon=False, ncol=2)
    # fig.savefig("../images/multiple_points.png")
    plt.show()


def main():
    sampling_interval = 0.001
    signal, events = create_data(sampling_interval)

    nixfile = nixio.File.open("multiple_points.nix", nixio.FileMode.Overwrite)
    block = nixfile.create_block("recording session", "nix.session")
    signal_array = block.create_data_array("signal", "nix.sampled", data=signal)
    signal_array.label = "voltage"
    signal_array.unit = "mV"
    signal_array.append_sampled_dimension(sampling_interval, label="time", unit="s")

    event_array = block.create_data_array("threshold crossings", "nix.events.threshold_crossings", data=events)
    event_array.label = "time"
    event_array.unit = "s"
    event_array.append_range_dimension_using_self()

    mtag = block.create_multi_tag("event tag", "nix.tag.events", event_array)
    mtag.references.append(signal_array)

    plot(mtag)
    nixfile.close()


if __name__ == "__main__":
    main()
