
import matplotlib.pyplot as plt
import numpy
import time
from datetime import datetime
from random import random
import numpy as np
import os
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
        self.correctedWavelengths = None
        self.correctedIntensities = None
        self.correctedIntegratedIntensity = 0
        self.completed = False
        self.startTime = None
        self.endTime = None
        self.average = average
        self.correctNonlinearity = correctNonlinearity
        self.correctDarkCounts = correctDarkCounts
        self.integratedIntensity = 0
    

    @staticmethod
    def completedDummy():
        """Get a completed measurement filled with random sine waves for debugging display
        """
        res = Measurement(random()*10,random()*100+120,1)
        res.temperature = random()*40-20
        res.wavelengths = np.linspace(120,900,1000)
        res.intensities = np.sin(res.wavelengths/(random()*50+10))
        res.startTime = datetime.now()
        res.endTime = datetime.now()
        res.calculateCorrected()
        res.completed = True
        return res


    def __str__(self):
        return f"{self.wavelength:.1f}nm"

    def baseline(self,level = 30):
        """Caculates zero offset of the intensities

        Parameter
        ---------
        level : float, default 30
            everything lower than this threshhold is considered noise and used to calculate the offset
        Return
        ------
        float : the baseline
        """
        return np.average(self.intensities[50:150][self.intensities[50:150]<=level]) # offset from zero, an average over some pixels at the start that are smaller than some expected level
    
    def calculateCorrected(self):
        self.correctedIntensities = self.intensities-self.baseline()
        convWidth = 10
        treshhold = 15
        conv = np.convolve(self.correctedIntensities,np.ones(convWidth)/convWidth,"same") # get a moving average
        good = np.where(abs(conv-self.correctedIntensities)< treshhold) # all pixels that deviate to far are removed
        self.correctedWavelengths = self.wavelengths[good]
        self.correctedIntensities = self.correctedIntensities[good]
        minIndex = np.argmax(self.correctedWavelengths>350) #wavelength range to integrate over
        maxIndex = np.argmax(self.correctedWavelengths>650)
        self.correctedIntegratedIntensity = np.trapz(self.correctedIntensities[minIndex:maxIndex],self.correctedWavelengths[minIndex:maxIndex]) # sum() does not work as the wavelength difference is not uniform anymore

    def measure(self, spec,main):
        self.wavelengths = spec.wavelengths()
        # The motor needs to be moved in between calls of this function, which is why you can't already set the integration time for the next measurement.
        # The intensities buffer would fill while the grating is moving, giving a fluorescence spectrum of mixed wavelengths
        spec.integration_time_micros(int(self.integrationtime*1_000_000)) #set next integration time
        spec.intensities()                                                #begin a new measurement with the desired integration time, dicard the values measured up to now
    
        total = None
        totaltemp = 0
        self.startTime = datetime.now()
        for x in range(self.average):
            main.currentAverage = x
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
        #self.calculateCorrected()
        self.integratedIntensity = sum(self.intensities)
        self.completed = True

    def getFilename(self,directory,fileformat):
        #TODO: %n does not work
        filename = fileformat
        filename = filename.replace("%wav",f"{self.wavelength:.1f}")
        filename = filename.replace("%date",self.startTime.strftime("%d_%m_%Y"))
        #filename = filename.replace("%n",f"{self.measurementCount}")
        filename = filename.replace("%time",self.startTime.strftime("%H-%M-%S"))
        return os.path.join(directory,filename)

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
    def measure(self, spec,main):
        self.wavelengths = np.linspace(120,900,1000)    
        total = None
        totaltemp = 0
        self.startTime = datetime.now()
        for x in range(self.average):
            main.currentAverage = x
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
        self.calculateCorrected()
        self.endTime = datetime.now()
        self.integratedIntensity = sum(self.intensities)
        self.completed = True