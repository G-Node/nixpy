import numpy as np
import nixio
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def create_example_data(nixfile):
    sampling_interval = 0.001
    total_duration = 3.0
    time = np.arange(0., total_duration, sampling_interval)
    stim = np.ones(time.shape)
    stim_duration = 0.25
    intervals = np.arange(0.25, total_duration, stim_duration * 3)
    stim_frequencies = np.zeros_like(intervals)
    stim_onsets = np.zeros_like(intervals)
    stim_extents = np.zeros_like(intervals)
    base_freq = 5

    for i, interval in enumerate(intervals):
        stim[(time >= interval) & (time < interval + stim_duration)] = i + 2
        stim_frequencies[i] = (i + 2) * base_freq
        stim_onsets[i] = interval
        stim_extents[i] = stim_duration
    stim *= base_freq
    signal = np.sin(time * 2 * np.pi * stim)

    block = nixfile.create_block("multiple regions", "nix.session")

    data_array = block.create_data_array("signal", "nix.data.sampled", data=signal)
    data_array.label = "voltage"
    data_array.unit = "mV"
    data_array.append_sampled_dimension(sampling_interval, label="time", unit="s")

    positions = block.create_data_array("stimulus onsets", "nix.region.onsets", data=stim_onsets)
    positions.append_set_dimension()

    extents = block.create_data_array("stimulus extents", "nix.region.extents", data=stim_extents)
    extents.append_set_dimension()

    frequencies = block.create_data_array("stimulus frequency", "nix.feature", data=stim_frequencies)
    frequencies.label = "frequency"
    frequencies.unit = "Hz"
    frequencies.append_set_dimension()

    mtag = block.create_multi_tag("stimulus segments", "nix.segments.stimulus", positions=positions, extents=extents)
    mtag.references.append(data_array)
    mtag.create_feature(frequencies, nixio.LinkType.Indexed)


def plot(nixfile):
    block = nixfile.blocks[0]
    signal_da = block.data_arrays["signal"]
    signal = signal_da[:]
    signal_dim = signal_da.dimensions[0]
    time = np.asarray(signal_dim.axis(len(signal)))
    mtag = block.multi_tags[0]
    fig = plt.figure()
    fig.set_size_inches(5.5, 2.5)
    ax = fig.add_subplot(111)

    l, = ax.plot(time, signal, label=signal_da.name)
    ax.set_xlim([0., 3.])
    ax.set_ylim([-1.45, 1.45])
    ax.set_xticks(np.arange(0., 3.01, 0.5))
    ax.set_yticks(np.arange(-1.5, 1.6, 0.5))
    ax.set_xlabel("%s %s" % (signal_dim.label, "[%s]" % signal_dim.unit if signal_dim.unit else ""))
    ax.set_ylabel("%s %s" % (signal_da.label, "[%s]" % signal_da.unit if signal_da.unit else ""))

    for i, (interval, extent) in enumerate(zip(mtag.positions[:], mtag.extents[:])):
        rect = patches.Rectangle((interval, 1.05), extent, -2.1, alpha=0.5,
                                 facecolor="silver", edgecolor='k', lw=0.75, ls='--')
        ax.add_patch(rect)
        ax.text(interval + extent / 2, -1.25,
                "%.1f %s" % (mtag.feature_data(i, "stimulus frequency")[:],
                             mtag.features["stimulus frequency"].data.unit), fontsize=8, ha="center")
    ax.legend((l, rect), (signal_da.name, mtag.name), loc=1, frameon=False, ncol=2)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.subplots_adjust(bottom=0.175, left=0.15, right=0.95, top=0.95)
    # fig.savefig("../images/multiple_regions.png")
    plt.show()


def plot_tagged_data(nixfile):
    block = nixfile.blocks[0]
    mtag = block.multi_tags[0]
    signal_da = mtag.references["signal"]
    signal_dim = signal_da.dimensions[0]
    xlabel = "%s %s" % (signal_dim.label, "[%s]" % signal_dim.unit if signal_dim.unit else "")
    ylabel = "%s %s" % (signal_da.label, "[%s]" % signal_da.unit if signal_da.unit else "")

    fig = plt.figure(figsize=(5.5, 2.5))
    num_segments = len(mtag.positions[:])
    for i in range(num_segments):
        data = mtag.tagged_data(i, "signal")[:]
        time = signal_dim.axis(len(data), start_position=mtag.positions[i])
        ax = fig.add_subplot(1, num_segments, i + 1)
        ax.plot(time, data)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlabel(xlabel)
        if i == 0:
            ax.set_ylabel(ylabel)
        else:
            ax.set_yticklabels([])
    fig.subplots_adjust(left=0.15, bottom=0.2, wspace=0.5, right=0.975)
    # fig.savefig("../images/reading_tagged_data.png")
    plt.show()


def main():
    nixfile = nixio.File.open("multiple_regions.nix", nixio.FileMode.Overwrite)

    create_example_data(nixfile)
    plot(nixfile)
    plot_tagged_data(nixfile)
    nixfile.close()


if __name__ == "__main__":
    main()
