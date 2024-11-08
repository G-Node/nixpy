import nixio
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

import docutils

interval = 0.001
duration = 3.5
stim_on = 0.5
stim_off = 2.5
stim_amplitude = 1.0


def butter_lowpass(highcut, fs, order=5):
    nyq = 0.5 * fs
    high = highcut / nyq
    b, a = signal.butter(order, high, btype='low')
    return b, a


def butter_highpass(lowcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    b, a = signal.butter(order, low, btype='high')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, lporder=1, hporder=1):
    lpb, lpa = butter_lowpass(highcut, fs, order=lporder)
    hpb, hpa = butter_highpass(lowcut, fs, order=hporder)
    y = signal.lfilter(lpb, lpa, data)
    y = signal.lfilter(hpb, hpa, y)
    return y


def plot(time, response):
    fig = plt.figure()
    fig.set_size_inches(5.5, 2.5)
    ax = fig.add_subplot(111)
    ax.plot(time, response, label="response")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("voltage [mV]")
    ax.plot([stim_on, stim_off], [1.0, 1.0], ls="solid", lw=2., color="red", label="stimulus on")
    ax.set_ylim([-1.2, 1.2])
    ax.set_yticks([-1., -0.5, 0, 0.5, 1.])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc=3, frameon=False)
    fig.subplots_adjust(left=0.15, bottom=0.175, right=0.95, top=0.95)
    # fig.savefig('../images/tag1.png')

    ax.scatter(stim_on, 1.15, marker="o", color='silver', lw=0.1)
    ax.plot([stim_on, stim_off], [1.15, 1.15], lw=0.5, color="silver")
    ax.plot([stim_off, stim_off], [1.1, 1.2], lw=0.5, color="silver")
    ax.text(1.3, 1.175, "extent")
    ax.annotate('position', xy=(stim_on, 1.15), xytext=(-0.15, 1.15),
                arrowprops=dict(facecolor='silver', connectionstyle="arc3", arrowstyle="->"),
                )
    # fig.savefig('../images/tag2.png')
    if docutils.is_running_under_pytest():
        plt.close()
    else:
        plt.show()


def create_data():
    time = np.arange(0., 3.5, interval)
    stimulus = np.zeros(time.shape)
    stimulus[(time >= stim_on) & (time < stim_off)] = stim_amplitude
    response = butter_bandpass_filter(stimulus, .25, 10., 1. / interval)
    return time, stimulus, response


def read_all_data(data_array):
    print(data_array.shape)
    data = data_array[:]
    time = data_array.dimensions[0].axis(len(data))
    return time, data


def main():
    time, _, response = create_data()

    f = nixio.File.open("tagging1.nix", nixio.FileMode.Overwrite)
    block = f.create_block("demo block", "nix.demo")
    data = block.create_data_array("response", "nix.sampled", data=response)
    data.label = "voltage"
    data.unit = "mV"

    data.append_sampled_dimension(interval, label="time", unit="s")

    stim_tag = block.create_tag("stimulus", "nix.stimulus_segment", position=[stim_on])
    stim_tag.extent = [stim_off - stim_on]
    stim_tag.references.append(data)

    plot(time, response)
    read_partial_data(data)
    f.close()


def read_partial_data(data_array):
    # let's read the 101 to 1000th element of the data
    partial_data = data_array[100:1000]
    time = data_array.dimensions[0].axis(900, 100)
    print(partial_data.shape, len(time))

    # using the get_slice method to get the data in the interval 0.5 to 1.75 s
    partial_data = data_array.get_slice([0.5], [1.25], nixio.DataSliceMode.Data)[:]
    time = np.arange(0.5, 0.5 + 1.25, data_array.dimensions[0].sampling_interval)
    print(partial_data.shape, len(time))


if __name__ == "__main__":
    main()
