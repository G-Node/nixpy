from neo import (Block, Segment,
                 AnalogSignal, IrregularlySampledSignal,
                 Event, Epoch, SpikeTrain,
                 ChannelIndex, Unit)
from neo.io.nixio import NixIO

import numpy as np
import quantities as pq



block1 = Block("nix-raw-block1", description="The 1st block")
block2 = Block("nix-raw-block2", description="The 2nd block")

for block in (block1, block2):
    ch_count = 0
    asig_count = 0
    nsegments = 2

    # Generate 3 fake data signals using numpy's random function
    # The shapes of the arrays are arbitrary
    data_a = np.random.random((300, 1)) # make the shape all the same, to make sure array generation is good
    # not sure if it is the general case
    data_b = np.random.random((1200, 3))
    data_c = np.random.random((8000, 5))
    nchannels = data_a.shape[1] + data_b.shape[1] + data_c.shape[1] # which one is correct
    nchannels = 3

    sampling_rate = pq.Quantity(1, "Hz")

    indexes = np.arange(nchannels)
    for cidx, signal in enumerate([data_a, data_b, data_c]):
        indexes = np.arange(signal.shape[1]) + ch_count
        ch_count += signal.shape[1]
        chx = ChannelIndex(name="channel-{}".format(cidx),
                           index=indexes,
                           channel_names=["S" + str(cidx) + chr(ord("a") + i) for i in indexes],
                           channel_ids=cidx * 100 + indexes + 1)
        block.channel_indexes.append(chx)

    for idx in range(nsegments):
        seg = Segment("seg-ex{}".format(idx),
                      description="Segment number {}".format(idx))
        block.segments.append(seg)

        # signal +idx is for testing if segment is correct
        for didx, data in enumerate((data_a, data_b, data_c)):
            if didx == 1:
                asig = AnalogSignal(name="Seg {} :: Data {}".format(idx, didx),
                                    signal=data+idx, units="V",
                                    sampling_rate=sampling_rate)
                print("Seg {} :: Data {}".format(idx, didx))
            else:
                asig = AnalogSignal(name="Seg {} :: Data {}".format(idx, didx),
                                signal=data+idx, units="mV",
                                sampling_rate=sampling_rate)
                print("Seg {} :: Data {}".format(idx, didx))
            seg.analogsignals.append(asig)
            block.channel_indexes[didx].analogsignals.append(asig)
        asig_count += len((data_a, data_b, data_c))

        # random sampling times for data_b
        irsigdata = np.random.random((1200, 2))
        itimes = np.cumsum(np.random.random(1200))

        # Create one AnalogSignal and one IrregularlySampledSignal
        isig = IrregularlySampledSignal(name="Sampled data", signal=irsigdata,
                                        units="nA",
                                        times=itimes, time_units="ms")
        seg.irregularlysampledsignals.append(isig)

        # Event, Epoch, SpikeTrain
        tstart = 10 * pq.ms
        event_times = tstart + np.cumsum(np.random.random(5)) * pq.ms
        event = Event(name="Seg {} :: Event".format(idx),
                      times=event_times,
                      labels=["A", "B", "C", "D", "E"])
        seg.events.append(event)

        epoch_times = tstart + np.cumsum(np.random.random(3)) * pq.ms
        epoch = Epoch(name="Seg {} :: Epoch".format(idx),
                      times=epoch_times,
                      durations=np.random.random(3)*pq.ms,
                      labels=["A+", "B+", "C+"])
        seg.epochs.append(epoch)

        st_times = tstart + np.cumsum(np.random.random(10)) * pq.ms
        tstop = max(event_times[-1], epoch_times[-1], st_times[-1]) + 1 * pq.ms
        st = SpikeTrain(name="Seg {} :: SpikeTrain".format(idx),
                        times=st_times, t_start=tstart, t_stop=tstop)
        wf = np.random.random((len(st_times), nchannels, 30)) * pq.mV
        st.waveforms = wf
        st.sampling_rate = sampling_rate

        seg.spiketrains.append(st)

        unit = Unit(name="unit-{}".format(idx))
        unit.spiketrains.append(st)
        chx.units.append(unit)

# Write the Block to file using the NixIO
# Any existing file will be overwritten
fname = "neoraw.nix"
io = NixIO(fname, "ow")
io.write_block(block1)
io.write_block(block2)
io.close()

print("Done. Saved to {}".format(fname))
