#!/usr/local/bin/python3.7

#pip3 install seabreeze
#
#pip3 install PyQt5
#pip3 install pyserial
#support: david.berger@tum.de
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QInputDialog, QCheckBox, QMessageBox,QFileDialog,QLineEdit, QComboBox, QPushButton, QLabel, QTextBrowser, QScrollBar, QApplication,QListWidget,QDoubleSpinBox,QSpinBox,QGroupBox,QVBoxLayout,QTabWidget
from PyQt5.QtCore import QSettings,pyqtSignal
import sys
import os
import serial
import serial.tools.list_ports
import seabreeze
import matplotlib.pyplot as plt
from seabreeze.spectrometers import list_devices, Spectrometer
from datetime import datetime

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

import time

from random import random

import threading

"""
IMPORTANT:
This took me an hour to find and an hour to fix as there is no documentation on this at all:

1. The Spectrometer *always* has an active measurement running, in a rolling buffer the length of the *current* integration time
1.1 As far as I know the current measurement can't be stopped to start a new one of desired length before the buffer is filled (at least from the SeaBreeze API).

2. spectrometer.intensities() returns the active measurement as soon as the buffer is filled, and *immediately* starts filling a new buffer of current integration time again
2.1 The function does not only read the current buffer as soon as available, it also starts a new measurement with the current integration time and therefore clears the buffer
2.2 If the time since the last call of spectrometer.intensities is longer than integration time, it immediately returns the current buffer,
    else the function waits for the buffer to fill back up, which can take up to the integration time.

3. spectrometer.integration_time_micros(microseconds) sets the current integration time, but *does not* change the current buffer size,
   so that the current integration time is only applied to the next *newly started* measurement (not the one currently running!)

4. At startup (i.e. the spectrometer newly connected to the PC) the current integration time is the minimum integration time.
   When only disconnected via software, the last integration time gets preserved, so it you should set it to a low value before disconnecting as the integration time can not be changed while the buffer is still filling.
   Leaving the spectrometer with an integration time of e.g. 10 minutes means that the next program to use it has to wait 10 minutes before it can start a new measurement of desired length. This can be circumvented by
   unplugging and plugging back in, as almost all problems concerning computers.
Example:
At the start of the example a newly connected spectrometer is assumed

spec.integration_time_micros(10_000_000) #10 seconds
result1 = spec.intensities()    #takes an unknown amount of time, returns the buffer that was instantiated with the *last* integration time,
                                #then creates a new measurement buffer with a capacity of the current integration time (here 10s)
result2 = spec.intensities()    #takes 10 second to execute
time.sleep(2)                   #sleep 2 seconds
spec.integration_time_micros(5_000_000) #5 seconds
result3 = spec.intensities()    #takes 8 seconds, as the buffer could already fill for two seconds in the background, and creates a new buffer with capacity for 5s
time.sleep(10)                  #do nothing for 10 seconds
result4 = spec.intensities()    #returns immediately
=>result1 contains the intensities of the integration period that is set as standard at startup of the spectrometer (or the last used before disconnecting?)
=>result2 contains a spectrum of the last 10 seconds
=>result3 contains a spectrum of the last 10 seconds
=>result4 contains a spectrum of the last 05 seconds
"""

#For debugging without access to spectrometer/motor
#ALWAYS set to False before commiting
motorDummy = True
spectrometerDummy = True

class Ui(QtWidgets.QMainWindow):

    #signals
    allMeasurementsComplete = pyqtSignal()
    measurementComplete = pyqtSignal(object)

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('mainWindow.ui', self)
        # constants
        self.timeout = 5  # in seconds

        # variables
        
        self.tabWidget = self.findChild(QTabWidget,'tabWidget')
        #config page
        self.comPortBox = self.findChild(QComboBox, 'comPortBox')
        self.specBox = self.findChild(QComboBox, 'specBox')
        self.connectArduButton = self.findChild(QPushButton, 'connectArduButton')
        self.connectSpecButton = self.findChild(QPushButton, 'connectSpecButton')
        self.specInfoLabel = self.findChild(QLabel, 'specInfoLabel')
        self.comLogBrowser = self.findChild(QTextBrowser, 'comLogBrowser')
        self.browseButton = self.findChild(QPushButton,'browseButton')
        self.outputEdit = self.findChild(QLineEdit,'outputEdit')
        self.fileEdit = self.findChild(QLineEdit,'fileEdit')
        self.saveCheckBox = self.findChild(QCheckBox,'saveCheckBox')
        self.calibrateRotationButton = self.findChild(QPushButton,'calibrateRotationButton')
        self.useSavedZeroButton = self.findChild(QPushButton,'useSavedZeroButton')
        self.useSavedCurrentButton = self.findChild(QPushButton,'useSavedCurrentButton')
        self.temperatureSpinBox = self.findChild(QDoubleSpinBox,'temperatureSpinBox')
        self.temperatureLabel = self.findChild(QLabel,'temperatureLabel')
        #measurement page
        self.startButton = self.findChild(QPushButton, 'startButton')
        self.addSingleButton = self.findChild(QPushButton,'addSingleButton')
        self.measurementList = self.findChild(QListWidget,'measurementList')
        self.fromSpinBox = self.findChild(QDoubleSpinBox, 'fromSpinBox')
        self.toSpinBox = self.findChild(QDoubleSpinBox,'toSpinBox')
        self.averageSpinBox = self.findChild(QSpinBox,'averageSpinBox')
        self.integrationSpinBox = self.findChild(QDoubleSpinBox,'integrationSpinBox')
        self.averageShowSpinBox = self.findChild(QSpinBox,'averageShowSpinBox')
        self.wavelengthShowSpinBox = self.findChild(QDoubleSpinBox,'wavelengthShowSpinBox')
        self.integrationShowSpinBox = self.findChild(QDoubleSpinBox,'integrationShowSpinBox')
        self.stepSpinBox = self.findChild(QDoubleSpinBox,'stepSpinBox')
        self.addGroupBox = self.findChild(QGroupBox,'addGroupBox')
        self.measurementsGroupBox = self.findChild(QGroupBox,'addGroupBox')
        self.infoGroupBox = self.findChild(QGroupBox,'infoGroupBox')
        self.removeButton = self.findChild(QPushButton,'removeButton')
        self.correctDarkCheckBox = self.findChild(QCheckBox,'correctDarkCheckBox')
        self.correctNonlinearCheckBox = self.findChild(QCheckBox,'correctNonlinearCheckBox')
        #results page
        self.resultsList = self.findChild(QListWidget,'resultsList')
        self.plotLayout = self.findChild(QVBoxLayout,'plotLayout')
        self.resultInfoLabel = self.findChild(QLabel,'resultInfoLabel')
        self.statusLabel = self.findChild(QLabel,'statusLabel')
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.plotLayout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()
        self.saveMeasurementButton = self.findChild(QPushButton,'saveMeasurementButton')
        self.savePlotButton = self.findChild(QPushButton,'savePlotButton')
        #settings
        self.settings = QSettings("TUM", "E15Spectrometer")
        #devices and connections
        self.ports = []
        self.currentPort = None
        self.devices = []
        self.ser = None
        self.spectrometer = None
        self.currentDevice = None
        self.motorControl = None
        #measurements
        self.pendingMeasurements = []
        self.completedMeasurements = []
        self.currentMeasurement = None
        self.measurementThread = None
        self.abortMeasurement = False
        self.updateTempThread = None
        self.measurementCount = 0
        self.selectedResults = []
        self.map = None
        self.miw = None
        self.maw = None

        # event triggers
        self.connectArduButton.clicked.connect(self.connectArduino)
        self.startButton.clicked.connect(self.startMeasuring)
        self.addSingleButton.clicked.connect(self.addSingle)
        self.addRangeButton.clicked.connect(self.addRange)
        self.wavelengthShowSpinBox.valueChanged.connect(self.showWavelengthChanged)
        self.averageShowSpinBox.valueChanged.connect(self.showAverageChanged)
        self.integrationShowSpinBox.valueChanged.connect(self.showIntegrationChanged)
        self.measurementList.itemSelectionChanged.connect(self.measurementChanged)
        self.resultsList.itemSelectionChanged.connect(self.resultChanged)
        self.removeButton.clicked.connect(self.removeMeasurement)
        self.comPortBox.currentIndexChanged.connect(self.comChanged)
        self.browseButton.clicked.connect(self.selectFolder)
        self.calibrateRotationButton.clicked.connect(self.calibrateRotation)
        self.useSavedCurrentButton.clicked.connect(self.useSavedCurrent)
        self.useSavedZeroButton.clicked.connect(self.useSavedZero)
        self.temperatureSpinBox.valueChanged.connect(self.setTargetTemp)
        self.saveMeasurementButton.clicked.connect(self.saveCurrentMeasurement)
        self.savePlotButton.clicked.connect(self.saveCurrentPlot)
        self.correctDarkCheckBox.stateChanged.connect(self.showElectricDarkChanged)
        self.correctNonlinearCheckBox.stateChanged.connect(self.showNonlinearityChanged)
        self.measurementComplete.connect(self.onMeasurementComplete)
        self.allMeasurementsComplete.connect(self.onAllMeasurementsComplete)
        # setup functions
        self.refreshComports()
        self.refreshSpectrometers()
        self.loadSettings()

        # finally, run the application
        self.show()

    def setTargetTemp(self,value):
        if self.spectrometer:
            self.spectrometer.features['thermo_electric'][0].set_temperature_setpoint_degrees_celsius(value)

    def updateTemp(self):
        while True:
            if self.spectrometer:
                self.temperatureLabel.setText(f"{self.spectrometer.features['thermo_electric'][0].read_temperature_degrees_celsius()}°C")
            else:
                self.temperatureLabel.setText("not connected")
            time.sleep(1)

    def calibrateRotation(self):
        if self.motorControl == None:
            QMessageBox.critical(self,"Motor control not connected","Please connect the motor control")
            return
        self.tabWidget.setEnabled(False)
        QMessageBox.information(self,"Step 1","The motor will now drive to the lower end of its range and save that position. Prepare to read the wavelength when it has arrived. This will take some time, the application might be unresponsive.\nPress ok to start!")
        self.motorControl.log("waiting for motor to arrive...")
        QApplication.processEvents()
        self.motorControl.findMinimumPosition()
        self.miw = QInputDialog.getDouble(self, "The motor has arrived!","Current Wavelength (not grating)")[0]
        print("miw",self.miw)
        QMessageBox.information(self,"Step 2","The motor will now drive to the upper end of its range and save that position. Prepare to read the wavelength when it has arrived. This will take some time, the application might be unresponsive.\nPress ok to start!")
        self.motorControl.log("waiting for motor to arrive...")
        QApplication.processEvents()
        self.map = self.motorControl.findMaximumPosition()
        self.maw = QInputDialog.getDouble(self, "The motor has arrived","Current Wavelength (not grating)")[0]
        print("maw",self.maw)
        QMessageBox.information(self,"Done","The calibration is complete")
        self.tabWidget.setEnabled(True)

    def useSavedZero(self):
        if self.motorControl == None:
            QMessageBox.critical(self,"Motor control not connected","Please connect the motor control")
            return
        if self.miw == None or self.maw ==None or self.map == None:
            QMessageBox.critical(self,"Not calibrated","Please calibrate first")
            return

        QMessageBox.information(self,"Setup","The motor will drive to zero position.\npress ok to start")
        self.tabWidget.setEnabled(False)
        self.motorControl.setWavelengthRange(self.miw,self.maw)
        self.motorControl.setMaxPosition(self.map)
        self.motorControl.findMinimumPosition()
        QMessageBox.information(self,"Setup","done!")
        self.tabWidget.setEnabled(True)

    def useSavedCurrent(self):
        if self.motorControl == None:
            QMessageBox.critical(self,"Motor control not connected","Please connect the motor control")
            return
        if self.miw == None or self.maw ==None or self.map == None:
            QMessageBox.critical(self,"Not calibrated","Please calibrate first")
            return
        self.motorControl.setWavelengthRange(self.miw,self.maw)
        self.motorControl.setMaxPosition(self.map)
        self.motorControl.setCurrentWavelength(QInputDialog.getDouble(self, "Setup","Current Wavelength (not grating)")[0])
        QMessageBox.information(self,"Setup","done!")

    def closing(self):
        self.saveSettings()
        self.cleanup()

    def comChanged(self, index):
        if index >= 0:
            self.currentPort = self.ports[index]

    def refreshComports(self):
        self.ports = serial.tools.list_ports.comports()
        self.comPortBox.addItems([port.device for port in self.ports])
        if motorDummy:
            self.motorControl = MotorControlDummy(self.comLogBrowser,0)

    def selectFolder(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec():
            self.outputEdit.setText(dialog.directory().absolutePath())

    def refreshSpectrometers(self):
        self.devices = list_devices()
        self.specBox.clear()
        self.specBox.addItems([spec.model for spec in self.devices])
        if(self.specBox.count()):
            self.cleanupSpectrometer()
            self.currentDevice = self.devices[self.specBox.currentIndex()]
            self.spectrometer = Spectrometer(self.currentDevice)
            wv = self.spectrometer.wavelengths()
            it = self.spectrometer.integration_time_micros_limits
            self.specInfoLabel.setText(
                f"Model:\t\t{self.spectrometer.model}\n\n"
                f"Serial Number:\t{self.spectrometer.serial_number}\n\n"
                f"Wavelength:\t{wv[0]:.0f}nm-{wv[-1]:.0f}nm\n\n"
                f"Integration Time\t{it[0]/1000000}s-{it[1]/1000000}s"
            )
            self.updateTempThread = threading.Thread(target=self.updateTemp, daemon=True)
            self.updateTempThread.start()

    def saveCurrentMeasurement(self):
        if len(self.selectedResults) != 1:
            QMessageBox.critical(self,"Can't save","Select a single measurement first")
            return
        filename = QFileDialog.getSaveFileName(self,"Save","","csv File (*.txt)")[0]
        if filename:
            self.selectedResults[0].save(filename)

    def saveCurrentPlot(self):
        filename = QFileDialog.getSaveFileName(self,"Save","","picture (*.png")[0]
        if filename:
            self.ax.figure.savefig(filename)

    def cleanupSpectrometer(self):
        if self.currentDevice and self.currentDevice.is_open:
            self.spectrometer.close()
        #TODO: cleanup temperature thread 

    def cleanup(self):
        del self.motorControl
        self.cleanupSpectrometer()

    def connectArduino(self):
        if not self.ports:
            QMessageBox.critical(self, "nothing connected","please connect the motor control")
            return
        self.currentPort = self.ports[self.comPortBox.currentIndex()]
        try:
            self.motorControl = MotorControl(self.currentPort,self.comLogBrowser)
        except Exception as e:
            QMessageBox.critical(self,"failed intitializing:",str(e))

    def addSingle(self):
        c = MeasurementDummy if spectrometerDummy else Measurement
        self.pendingMeasurements.append(c(self.integrationSpinBox.value(),self.fromSpinBox.value(),self.averageSpinBox.value()))
        self.pendingMeasurements.sort(key=lambda x:x.wavelength)
        self.measurementList.clear()
        self.measurementList.addItems([str(m) for m in self.pendingMeasurements])
    
    def addRange(self):
        c = MeasurementDummy if spectrometerDummy else Measurement
        for x in np.arange(self.fromSpinBox.value(),self.toSpinBox.value()+self.stepSpinBox.value(),self.stepSpinBox.value()):
            self.pendingMeasurements.append(c(self.integrationSpinBox.value(),x,self.averageSpinBox.value()))
        self.pendingMeasurements.sort(key= lambda x:x.wavelength)
        self.measurementList.clear()
        self.measurementList.addItems([str(m) for m in self.pendingMeasurements])
    
    def removeMeasurement(self):
        currentRow= self.measurementList.currentRow()
        if self.currentMeasurement and currentRow >=0:
            self.measurementList.takeItem(currentRow)
            self.pendingMeasurements.pop(currentRow)

    def showElectricDarkChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.correctDarkCounts = bool(value)
    def showNonlinearityChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.correctNonlinearity = bool(value)
    def showWavelengthChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.wavelength = value
    def showAverageChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.average = value
    def showIntegrationChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.integrationtime = value
    
    def resultChanged(self):
        selectedIndices = self.resultsList.selectionModel().selectedIndexes()
        self.selectedResults = [self.completedMeasurements[i.row()] for i in selectedIndices]
        if len(self.selectedResults)==1:
            tmp = self.selectedResults[0]
            self.resultInfoLabel.setText(
                f"Wavelength:\t{tmp.wavelength}nm\n\n"
                f"Integration Time:\t{tmp.integrationtime}s\n\n"
                f"Averages:\t{tmp.average}\n\n"
                f"Temperature\t{tmp.temperature}°C\n\n"
                f"Start:\t\t{tmp.startTime}\n\n"
                f"End:\t\t{tmp.endTime}\n\n"
                f"Integrated Intensity\t{tmp.integratedIntensity}\n\n"
                )
        else:
            self.resultInfoLabel.setText("Select a single measurement to display its properties")
        self.ax.clear()
        self.ax.set_ylabel("Count")
        self.ax.set_xlabel("Wavelength [nm]")
        for m in self.selectedResults:
            self.ax.plot(m.wavelengths,m.intensities,label=str(m.wavelength))
        self.ax.grid()
        if self.selectedResults:
            self.ax.legend()
        self.ax.figure.canvas.draw()
    
    def measurementChanged(self):
        currentRow = self.measurementList.currentRow()
        if len(self.pendingMeasurements) > currentRow >= 0:
            self.currentMeasurement = self.pendingMeasurements[currentRow]
            self.averageShowSpinBox.setValue(self.currentMeasurement.average)
            self.integrationShowSpinBox.setValue(self.currentMeasurement.integrationtime)
            self.wavelengthShowSpinBox.setValue(self.currentMeasurement.wavelength)
            self.correctDarkCheckBox.setCheckState(self.currentMeasurement.correctDarkCounts*2)
            self.correctNonlinearCheckBox.setCheckState(self.currentMeasurement.correctNonlinearity*2)
        else:
            self.currentMeasurement = None

    def onMeasurementComplete(self,measurement):
        self.measurementList.takeItem(0)
        self.completedMeasurements.append(measurement)
        self.resultsList.addItem(str(measurement))
        if(self.saveCheckBox.checkState()!=0): #save this measurement if autosave checkbox is ticked
            try:
                filename = self.fileEdit.text()
                directory = self.outputEdit.text()
                filename = filename.replace("%wav",f"{measurement.wavelength:.1f}")
                filename = filename.replace("%date",measurement.startTime.strftime("%d_%m_%Y"))
                filename = filename.replace("%n",f"{self.measurementCount}")
                filename = filename.replace("%time",measurement.startTime.strftime("%H-%M-%S"))
                path = os.path.join(directory,filename)
                dirname = os.path.dirname(path)
                if not os.path.exists(dirname):
                    os.mkdir(dirname)
                print(f"saving to {path}")
                measurement.save(path)
            except Exception as e:
                print("failed to save:" ,e)
        self.measurementCount +=1

    def onAllMeasurementsComplete(self):
        self.measurementsGroupBox.setEnabled(True)
        self.addGroupBox.setEnabled(True)
        self.infoGroupBox.setEnabled(True)
        self.startButton.setText("Start Measurement")

    def measureAll(self):
        while self.pendingMeasurements and not self.abortMeasurement:
            cur = self.pendingMeasurements.pop(0)
            try:
                self.motorControl.goToWavelength(cur.wavelength)
                cur.measure(self.spectrometer,self.statusLabel)
            except Exception as e:
                print("Measurement failed:",e)
            if cur.completed:
                self.measurementComplete.emit(cur)
        self.allMeasurementsComplete.emit()

    def startMeasuring(self):
        if self.measurementThread and self.measurementThread.is_alive():
            self.abortMeasurement = True
            return
        if self.motorControl == None:
            QMessageBox.critical(self,"Can't Start","Motor control not connected!")
            return
        if self.spectrometer == None and not spectrometerDummy:
            QMessageBox.critical(self,"Can't Start","Spectrometer not connected!")
            return
        if not self.pendingMeasurements:
            QMessageBox.information(self,"Can't Start","No measurements configured!")
            return
        self.abortMeasurement = False
        self.measurementsGroupBox.setEnabled(False)
        self.addGroupBox.setEnabled(False)
        self.infoGroupBox.setEnabled(False)
        self.startButton.setText("Stop Measurement")
        self.tabWidget.setCurrentIndex(1)
        self.measurementThread = threading.Thread(target=self.measureAll, daemon=True)
        self.measurementThread.start()
        
    def saveSettings(self):
        if self.currentPort:
            self.settings.setValue("COMPort", self.currentPort.device)
        self.settings.setValue("from",self.fromSpinBox.value())
        self.settings.setValue("to",self.toSpinBox.value())
        self.settings.setValue("step",self.stepSpinBox.value())
        self.settings.setValue("integration",self.integrationSpinBox.value())
        self.settings.setValue("average",self.averageSpinBox.value())
        self.settings.setValue("dir",self.outputEdit.text())
        self.settings.setValue("filename",self.fileEdit.text())
        self.settings.setValue("autosave",self.saveCheckBox.checkState())
        self.settings.setValue("targetTemp",self.temperatureSpinBox.value())
        if self.miw != None:
            self.settings.setValue("miw",self.miw)
        if self.maw != None:
            self.settings.setValue("maw",self.maw)
        if self.map != None:
            self.settings.setValue("map",self.map)
        self.settings.sync()
    
    def loadSettings(self):
        portsNames = [port.device for  port in self.ports]
        desiredPort = self.settings.value("COMPort")
        if (desiredPort and desiredPort in portsNames):
            self.comPortBox.setCurrentText(desiredPort)
        self.loadSpinBox("from",self.fromSpinBox)
        self.loadSpinBox("to",self.toSpinBox)
        self.loadSpinBox("step",self.stepSpinBox)
        self.loadSpinBox("integration",self.integrationSpinBox)
        self.loadSpinBox("average",self.averageSpinBox)
        self.loadSpinBox("targetTemp",self.temperatureSpinBox)
        self.loadText("dir",self.outputEdit)
        self.loadText("filename",self.fileEdit)
        self.loadCheckBox("autosave",self.saveCheckBox)
        self.miw = self.loadFloat("miw")
        self.maw = self.loadFloat("maw")
        self.map = self.loadFloat("map")
    
    def loadFloat(self,name):
        tmp = self.settings.value(name)
        if tmp != None:
            return float(tmp)
        return None

    def loadSpinBox(self,name,widget):
        tmp = self.settings.value(name)
        if tmp != None:
            widget.setValue(float(tmp))
    def loadText(self,name,widget):
        tmp = self.settings.value(name)
        if tmp != None:
            widget.setText(tmp)
    def loadCheckBox(self,name,widget):
        tmp = self.settings.value(name)
        if tmp!= None:
            widget.setCheckState(tmp)

class MotorControl:
    def __init__(self,port,logBrowser,timeout = 250):
        self.ser = serial.Serial(port.device, timeout=timeout)
        self.logBrowser = logBrowser
        if self.ser.is_open:
            self.log(f"opened on {self.ser.port}...")
            QApplication.processEvents()
            response = self.ser.readline().decode()
            if response:
                self.log(response)
            else:
                self.log("Motor does not respond")
                raise Exception("Motor does not respond")
        else:
            self.log("COM port can't be opened")
            raise Exception("COM port can't be opened")
        self.is_open = True

    def getResponse(self):
        response = self.ser.readline().decode()
        response = response.strip('\r\n')
        if response:
            self.log(response)
            if response[:5] == "error":
                raise Exception(response)
        else:
            self.log("Motor does not respond")
            raise Exception("Motor does not respond")
        return response

    def findMinimumPosition(self):
        self.sendCommand("fmi",0)

    def findMaximumPosition(self):
        response = self.sendCommand("fma",0)
        return int(response.lstrip("maximum set to "))

    def log(self, message):
        print(message)
        #NOT THREAD SAFE
        #self.logBrowser.append(str(message))
        #s = self.logBrowser.verticalScrollBar()
        #s.setValue(s.maximum())

    def sendCommand(self,command,value = 0):
        self.ser.write(f"${command} {float(value)}".encode())
        return self.getResponse()

    def goToWavelength(self,wavelength):
        self.sendCommand("gtw",wavelength)

    def setWavelengthRange(self,minlength,maxlength):
        self.sendCommand("miw",minlength)
        self.sendCommand("maw",maxlength)
    def setMaxPosition(self,position):
        self.sendCommand("map",position)
    def setCurrentWavelength(self,wavelength):
        self.sendCommand("caw",wavelength)
    def cleanup(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
    def __del__(self):
        self.cleanup()

#A dummy class to test when no motor is available
#simulates time delay waiting for response
#always returns no error on the motor part
#does not simulate connection issues at the moment
class MotorControlDummy(MotorControl):
    def __init__(self,logBrowser,timescale = 1):
        self.logBrowser = logBrowser
        self.log("opened on DUMMYPORT")
        self.timescale = timescale
        self.delay(1)
        self.log("connected and ready!")
        self.is_open = True
        self.commands = {"gtp":(1,"yey")}

    def delay(self,duration):
        time.sleep(duration*self.timescale)

    def getResponse(self,command):
        if command not in self.commands:
            return "error"
        self.delay(self.commands[command][0])
        return self.commands[command][1]

    def findMinimumPosition(self):
        self.sendCommand("fmi",0)

    def findMaximumPosition(self):
        response = self.sendCommand("fma",0)
        return int(response.lstrip("maximum set to "))


    def sendCommand(self,command,value = 0):
        self.log(f"Simulating:${command} {float(value)}")
        return self.getResponse(command)
    def cleanup(self):
        pass
    


class Measurement:
    def __init__(self, integrationtime, wavelength, average=1,correctNonlinearity = True,correctDarkCounts = True):
        self.integrationtime = integrationtime  # in seconds
        self.wavelength = wavelength  # in nanometers
        self.temperature = None
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
        #spec.features['thermo_electric'][0].set_temperature_setpoint_degrees_celsius(-20)
    
        total = None
        totaltemp = 0
        self.startTime = datetime.now()
        for x in range(self.average):
            statusLabel.setText(f"measuring {self.wavelength:.1f}nm {self.integrationtime}s {x+1}/{self.average}...")
            QApplication.processEvents()
            if x== 0:
                total = spec.intensities(
                    correct_dark_counts=True, correct_nonlinearity=True)
            else:
                if x == self.average-1:         # last spectrum
                    spec.integration_time_micros(spec.integration_time_micros_limits[0])  # set to the minimum while not measuring, applies after the next (and last) measurement
                total += spec.intensities(correct_dark_counts=self.correctDarkCounts,
                                          correct_nonlinearity=self.correctNonlinearity)
            totaltemp += spec.features['thermo_electric'][0].read_temperature_degrees_celsius()
        self.temperature = totaltemp/self.average
        self.intensities = total/self.average
        self.endTime = datetime.now()
        self.integratedIntensity = sum(self.intensities)
        statusLabel.setText("done!") #This is a slot, so it should be threadsafe
        self.completed = True

    def save(self,path):
        header = f"Wavelength (experimental): {self.wavelength}\n"\
                 f"Start Time: {self.startTime}\n"\
                 f"End Time: {self.endTime}\n"\
                 f"Integration Time [s]: {self.integrationtime}\n"\
                 f"Scans to average: {self.average}\n"\
                 f"Electric dark correction enabled: {self.correctDarkCounts}\n"\
                 f"Nonlinearity correction enabled: {self.correctNonlinearity}\n"\
                 f"Average temperature: {self.temperature}°C"
        np.savetxt(path,np.array((self.wavelengths,self.intensities)).transpose(),fmt = "%.3f",header = header)


class MeasurementDummy(Measurement):
    def measure(self, spec,statusLabel):
        self.wavelengths = np.linspace(120,900,1000)    
        total = None
        totaltemp = 0
        self.startTime = datetime.now()
        for x in range(self.average):
            statusLabel.setText(f"Simulating:measuring {self.wavelength:.1f}nm {self.integrationtime}s {x+1}/{self.average}...")
            QApplication.processEvents()
            if x== 0:
                #just random sines
                time.sleep(self.integrationtime)
                total = np.sin(self.wavelengths/(random()*50+10))
            else:
                time.sleep(self.integrationtime)
                total += np.sin(self.wavelengths/(random()*50+10))
            totaltemp += -25+random()*3
        self.temperature = totaltemp/self.average
        self.intensities = total/self.average
        self.endTime = datetime.now()
        self.integratedIntensity = sum(self.intensities)
        statusLabel.setText("done!")
        self.completed = True
app = QApplication(sys.argv)
window = Ui()
app.aboutToQuit.connect(window.closing)
sys.exit(app.exec_())