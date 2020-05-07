
import matplotlib.pyplot as plt
import numpy
import time
from datetime import datetime
from random import random
import numpy as np
from PyQt5.QtWidgets import QApplication

class Measurement:
    def __init__(self, integrationtime, wavelength, average=1,correctNonlinearity = True,correctDarkCounts = True):
        self.integrationtime = integrationtime  # in seconds
        self.wavelength = wavelength  # in nanometers
        self.temperature = None
        self.minTemp = 0
        self.maxTemp = 0
        self.wavelengths = None
        self.intensities = None
        self.completed = False
        self.startTime = None
        self.endTime = None
        self.average = average
        self.correctNonlinearity = correctNonlinearity
        self.correctDarkCounts = correctDarkCounts
        self.integratedIntensity = 0
    

    @staticmethod
    def completedDummy():
        #For having a completed measurement to test plotting etc.
        res = Measurement(random()*10,random()*100+120,1)
        res.temperature = random()*40-20
        res.wavelengths = np.linspace(120,900,1000)
        res.intensities = np.sin(res.wavelengths/(random()*50+10))
        res.startTime = datetime.now()
        res.endTime = datetime.now()
        res.completed = True
        return res


    def __str__(self):
        return f"{self.wavelength:.1f}nm"

    def display(self):
        if not self.completed:
            return
        avgs = self.average + "x" if self.average > 1 else ""
        plt.title(f"{self.startTime}:{avgs}{self.integrationtime}s @{self.wavelength}nm @{self.temperature}°C")
        plt.plot(self.wavelengths, self.intensities)
        plt.grid()
        plt.show()

    def measure(self, spec,statusLabel):
        self.wavelengths = spec.wavelengths()
        # The motor needs to be moved in between calls of this function, which is why you can't already set the integration time for the next measurement.
        # The intensities buffer would fill while the grating is moving, giving a fluorescence spectrum of mixed wavelengths
        spec.integration_time_micros(int(self.integrationtime*1_000_000)) #set next integration time
        spec.intensities()                                                #begin a new measurement with the desired integration time, dicard the values measured up to now
    
        total = None
        totaltemp = 0
        self.startTime = datetime.now()
        for x in range(self.average):
            statusLabel.setText(f"{self.wavelength:.1f}nm {self.integrationtime}s {x+1}/{self.average}...")
            QApplication.processEvents()
            temp = spec.features['thermo_electric'][0].read_temperature_degrees_celsius()
            if x == self.average-1:         # last spectrum
                spec.integration_time_micros(spec.integration_time_micros_limits[0])  # set to the minimum while not measuring, applies after the next (and last) measurement
            if x== 0:
                total = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
                self.minTemp = temp
                self.maxTemp = temp
            else:
                total += spec.intensities(correct_dark_counts=self.correctDarkCounts,
                                          correct_nonlinearity=self.correctNonlinearity)
                if temp < self.minTemp:
                    self.minTemp = temp
                if temp > self.maxTemp:
                    self.maxTemp = temp
            totaltemp += temp
        self.temperature = totaltemp/self.average
        self.intensities = total/self.average
        self.endTime = datetime.now()
        self.integratedIntensity = sum(self.intensities)
        statusLabel.setText("done!") #This is a slot, so it should be threadsafe
        self.completed = True

    def getHeader(self):
        return  \
f"""Wavelength:\t\t\t{self.wavelength}nm
Start Time:\t\t\t{self.startTime:%d.%m.%Y %H:%M:%S}
End Time:\t\t\t{self.endTime:%d.%m.%Y %H:%M:%S}
Integration Time:\t\t\t{self.integrationtime}s
Scans to average:\t\t\t{self.average}
Electric dark correction enabled:\t{self.correctDarkCounts}
Nonlinearity correction enabled:\t{self.correctNonlinearity}
Average temperature:\t\t{self.temperature:.1f}°C
Temperature spread:\t\t{self.minTemp:.1f} to {self.maxTemp:.1f}°C"""

    def save(self,path):
        header = self.getHeader()
        np.savetxt(path,np.array((self.wavelengths,self.intensities)).transpose(),fmt = "%.3f",header = header)


class MeasurementDummy(Measurement):
    def measure(self, spec,statusLabel):
        self.wavelengths = np.linspace(120,900,1000)    
        total = None
        totaltemp = 0
        self.startTime = datetime.now()
        for x in range(self.average):
            statusLabel.setText(f"{self.wavelength:.1f}nm {self.integrationtime}s {x+1}/{self.average}...")
            temp = -25+random()*3
            if x== 0:
                #just random sines
                time.sleep(self.integrationtime)
                total = random()*np.sin(self.wavelengths/(random()*50+10))
                self.minTemp = temp
                self.maxTemp = temp
            else:
                time.sleep(self.integrationtime)
                total += random()*np.sin(self.wavelengths/(random()*50+10))
                if temp < self.minTemp:
                    self.minTemp = temp
                if temp > self.maxTemp:
                    self.maxTemp = temp
            totaltemp += temp
        self.temperature = totaltemp/self.average
        self.intensities = total/self.average
        self.endTime = datetime.now()
        self.integratedIntensity = sum(self.intensities)
        statusLabel.setText("done!")
        self.completed = True