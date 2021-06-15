import nixio
import numpy as np


def create_data(duration, interval):
    times = np.around(np.cumsum(np.random.poisson(2.0 * 1000, int(1.5 * duration / interval))) / 1000., 3)
    times = times[times < duration]
    return times


def main():
    event_times = create_data(10., 1.0)
    nixfile = nixio.File.open("range_link.nix", nixio.FileMode.Overwrite)
    b = nixfile.create_block("session", "nix.session")

    data_array = b.create_data_array("event times", "nix.event.times", data=event_times)
    data_array.label = "time"
    data_array.unit = "s"
    data_array.append_range_dimension_using_self()

    nixfile.close()


if __name__ == "__main__":
    main()