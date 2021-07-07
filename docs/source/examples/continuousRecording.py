import nixio
import numpy as np
import matplotlib.pyplot as plt


def record_data(samples, channels, dt):
    data = np.zeros((samples, channels))
    t = np.arange(samples) * dt
    for i in range(channels):
        phase = i * 2 * np.pi / channels
        data[:, i] = np.sin(2 * np.pi * t + phase) + (np.random.randn(samples) * 0.1)

    return data


def plot(data_array):
    plot_samples = 5000
    channel_count = data_array.shape[1]

    time = data_array.dimensions[0].axis(plot_samples)
    dt = data_array.dimensions[0].sampling_interval
    labels = data_array.dimensions[1].labels
    data = data_array[:plot_samples, :]

    fig = plt.figure(figsize=(5, 2.5))
    for channel in range(channel_count):
        axis = fig.add_subplot(channel_count, 1, channel + 1)
        axis.plot(time, data[:, channel], label=labels[channel], lw=0.2)
        for sp in axis.spines.keys():
            axis.spines[sp].set_visible(False)
        axis.set_xticks([])
        axis.set_yticks([])
        axis.set_ylim([-2, 2])
        axis.text(0.0, 0.5, labels[channel], rotation=0, fontsize=8, ha="right", transform=axis.transAxes)

    axis.spines["bottom"].set_visible(True)
    axis.set_xticks(np.arange(0, plot_samples * dt + dt, plot_samples / 5 * dt, dtype=int))
    axis.set_xlabel("%s %s" % (data_array.dimensions[0].label, "[%s]" % data_array.dimensions[0].unit if data_array.dimensions[0].unit else ""))
    fig.subplots_adjust(left=0.15, bottom=0.175, top=0.975, right=0.975)
    plt.show()


def main():
    dt = 0.001
    chunk_samples = 1000
    number_of_channels = 10
    number_of_chunks = 100

    nixfile = nixio.File.open("continuous_recording.nix", nixio.FileMode.Overwrite, compression=nixio.Compression.DeflateNormal)
    block = nixfile.create_block("Session 1", "nix.recording_session")
    data_array = block.create_data_array("multichannel_data", "nix.sampled.multichannel", dtype=nixio.DataType.Double,
                                         shape=(chunk_samples, number_of_channels), label="voltage", unit="mV")
    data_array.append_sampled_dimension(0.001, label="time", unit="s")
    data_array.append_set_dimension(labels=["channel %i" % i for i in range(number_of_channels)])

    chunks_recorded = 0
    while chunks_recorded < number_of_chunks:
        data = record_data(chunk_samples, number_of_channels, dt)
        if chunks_recorded == 0:
            data_array.write_direct(data)
        else:
            data_array.append(data, axis=0)
        chunks_recorded += 1
        print("recorded chunks %i: array shape %s" % (chunks_recorded, str(data_array.shape)))

    plot(data_array)
    nixfile.close()

if __name__ == "__main__":
    main()
