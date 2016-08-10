# -*- coding: utf-8 -*-
"""
 Copyright © 2014 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>
"""
import numpy as np


class LIF(object):

    def __init__(self, stepsize=0.0001, offset=1.6, tau_m=0.025, tau_a=0.02, da=0.0, D=3.5):
        self.stepsize = stepsize  # simulation stepsize [s]
        self.offset = offset  # offset curent [nA]
        self.tau_m = tau_m  # membrane time_constant [s]
        self.tau_a = tau_a  # adaptation time_constant [s]
        self.da = da  # increment in adaptation current [nA]
        self.D = D  # noise intensity
        self.v_threshold = 1.0  # spiking threshold
        self.v_reset = 0.0  # reset voltage after spiking
        self.i_a = 0.0  # current adaptation current
        self.v = self.v_reset  # current membrane voltage
        self.t = 0.0  # current time [s]
        self.membrane_voltage = []
        self.spike_times = []

    def _reset(self):
        self.i_a = 0.0
        self.v = self.v_reset
        self.t = 0.0
        self.membrane_voltage = []
        self.spike_times = []

    def _lif(self, stimulus, noise):
        """
        euler solution of the membrane equation with adaptation current and noise
        """
        self.i_a -= self.i_a - self.stepsize/self.tau_a * (self.i_a)
        self.v += self.stepsize * ( -self.v + stimulus + noise + self.offset - self.i_a)/self.tau_m;
        self.membrane_voltage.append(self.v)

    def _next(self, stimulus):
        """
        working horse which delegates to the euler and gets the spike times
        """
        noise = self.D * (float(np.random.randn() % 10000) - 5000.0)/10000
        self._lif(stimulus, noise)
        self.t += self.stepsize
        if self.v > self.v_threshold and len(self.membrane_voltage) > 1:
            self.v = self.v_reset
            self.membrane_voltage[len(self.membrane_voltage)-1] = 2.0
            self.spike_times.append(self.t)
            self.i_a += self.da

    def run_const_stim(self, steps, stimulus):
        """
        lif simulation with constant stimulus.
        """
        self._reset()
        for i in range(steps):
            self._next(stimulus);
        time = np.arange(len(self.membrane_voltage))*self.stepsize
        return time, np.array(self.membrane_voltage), np.array(self.spike_times)

    def run_stimulus(self, stimulus):
        """
        lif simulation with a predefined stimulus trace.
        """
        self._reset()
        for s in stimulus:
            self._next(s);
        time = np.arange(len(self.membrane_voltage))*self.stepsize
        return time, np.array(self.membrane_voltage), np.array(self.spike_times)

    def __str__(self):
        out = '\n'.join(["stepsize: \t" + str(self.stepsize),
                         "offset:\t\t" + str(self.offset),
                         "tau_m:\t\t" + str(self.tau_m),
                         "tau_a:\t\t" + str(self.tau_a),
                         "da:\t\t" + str(self.da),
                         "D:\t\t" + str(self.D),
                         "v_threshold:\t" + str(self.v_threshold),
                         "v_reset:\t" + str(self.v_reset)])
        return out

    def __repr__(self):
        return self.__str__()
