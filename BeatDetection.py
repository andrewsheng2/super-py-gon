# Beat detection and frequency detection algorithm

import numpy as np

# Beat detection algorithm steps and formulas from
# http://archive.gamedev.net/archive/reference/programming/features/beatdetection/index.html
# (Simple sound energy algorithm #3)
# Modified to add FFT and frequency detection

class BeatDetection():

    def __init__(self, history=43):
        # 43 history values of 1024 samples is equivalent to 1 second in real time
        self.energyHistory = np.zeros(history) # will be used to store energy values
        self.energyHistoryIndex = 0 # the index of the oldest element
        self.lastFrequency = 0

    def detectBeat(self, data):

        signal = np.fromstring(data, dtype=np.int16)

        samples = signal.astype(np.int) # convert pyaudio information to integers
        # formula R1 from website
        instantEnergy = np.dot(samples, samples)

        # instead of formulas R3 and R4, we can use built in numpy methods
        energyAverage = self.energyHistory.mean()
        energyVariance = self.energyHistory.var()

        # formula R5 / R6 from website
        beatSensibility = (-0.0025714 * energyVariance) + 1.15142857

        # instead of shifting the energy values to make room for the new one, 
        # we can just replace the oldest energy value with the latest one
        # since ordering of our energy values does not really matter
        self.energyHistory[self.energyHistoryIndex] = instantEnergy
        self.energyHistoryIndex -= 1
        if self.energyHistoryIndex < 0:
            self.energyHistoryIndex = len(self.energyHistory) - 1

        # will result in True or False
        isBeat = instantEnergy > beatSensibility * energyAverage

        if isBeat and len(samples) != 0:
            # if current signaL is a beat, do a FFT and find dominant frequency
            fftData = np.fft.fft(samples)
            fftFreqs = np.fft.fftfreq(len(fftData))
            index = np.argmax(np.abs(fftData))
            frequency = abs(fftFreqs[index] * 44100)
            self.lastFrequency = frequency
        else:
            frequency = self.lastFrequency

        return (isBeat, frequency)