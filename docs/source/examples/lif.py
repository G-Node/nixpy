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

class lif:
    
    def __init__(self, stepsize=0.0001, offset=1.6, tau_m=0.025, tau_a=0.02, da=0.0, D=3.5):
        self.stepsize = stepsize # simulation stepsize [s]
        self.offset = offset # offset curent [nA]
        self.tau_m = tau_m # membrane time_constant [s]
        self.tau_a = tau_a # adaptation time_constant [s]
        self.da = da # increment in adaptation current [nA]
        self.D = D # noise intensity
        self.v_threshold = 1.0 # spiking threshold
        self.v_reset = 0.0 # reset voltage after spiking
        self.i_a = 0.0 # current adaptation current 
        self.v = self.v_reset # current membrane voltage
        self.t = 0.0 # current time [s] 
        self.membrane_voltage = []
        self.spike_times = []


    def reset(self):
        self.i_a = 0.0
        self.v = self.v_reset
        self.t = 0.0
        self.membrane_voltage = []
        self.spike_times = []
    

    def lif(self, stimulus, noise):
        """
        euler solution of the membrane equation with adaptation current and noise
        """
        self.i_a -= self.i_a - self.stepsize/self.tau_a * (self.i_a)
        self.v += self.stepsize * ( -self.v + stimulus + noise + self.offset - self.i_a)/self.tau_m; 
        self.membrane_voltage.append(self.v)


    def next(self, stimulus):
        """
        working horse which delegates to the euler and gets the spike times
        """
        noise = self.D * (float(np.random.randn() % 10000) - 5000.0)/10000
        self.lif(stimulus, noise)
        self.t += self.stepsize
        if self.v > self.v_threshold and len(self.membrane_voltage) > 1:
            self.v = self.v_reset
            self.membrane_voltage[len(self.membrane_voltage)-1] = 2.0
            self.spike_times.append(self.t)
            self.i_a += self.da;
  
    
    def run_const_stim(self, steps, stimulus):
        """
        lif simulation with constant stimulus.
        """
        self.reset()
        for i in range(steps):
            self.next(stimulus);
        time = np.arange(len(self.membrane_voltage))*self.stepsize
        return time, np.array(self.membrane_voltage), np.array(self.spike_times)


    def run_stimulus(self, stimulus):
        """
        lif simulation with a predefined stimulus trace.
        """
        self.reset()
        for s in stimulus:
            self.next(s);
        time = np.arange(len(self.membrane_voltage))*self.stepsize
        return time, np.array(self.membrane_voltage), np.array(self.spike_times)
