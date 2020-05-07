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
from datetime import datetime,timedelta

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

import time
from random import random
import threading

from dependencies.MotorControl import *
from dependencies.Measurement import *
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

motorDummy = False
spectrometerDummy = False

class Ui(QtWidgets.QMainWindow):

    #signals
    allMeasurementsComplete = pyqtSignal()
    measurementComplete = pyqtSignal(object)

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('dependencies/mainWindow.ui', self)
        if "dbgs" in sys.argv:
            global spectrometerDummy
            spectrometerDummy = True
            print("Debug mode: spectrometer dummy used.")
        if "dbgm" in sys.argv:
            global motorDummy
            motorDummy = True
            print("Debug mode: motorcontrol dummy used.")
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
        self.useSavedCurrentButton = self.findChild(QPushButton,'useSavedCurrentButton')
        self.temperatureSpinBox = self.findChild(QDoubleSpinBox,'temperatureSpinBox')
        self.temperatureLabel = self.findChild(QLabel,'temperatureLabel')
        self.offsetSpinBox = self.findChild(QDoubleSpinBox,'offsetSpinBox')
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
        self.estTimeLabel = self.findChild(QLabel,'estTimeLabel')
        self.sortButton = self.findChild(QPushButton,'sortButton')
        #results page
        self.resultsList = self.findChild(QListWidget,'resultsList')
        self.plotLayout = self.findChild(QVBoxLayout,'plotLayout')
        self.integratedPlotLayout = self.findChild(QVBoxLayout,'integratedPlotLayout')
        self.resultInfoLabel = self.findChild(QLabel,'resultInfoLabel')
        self.statusLabel = self.findChild(QLabel,'statusLabel')
        self.simplePlotCanvas = FigureCanvas(Figure())
        self.integratedPlotCanvas = FigureCanvas(Figure())
        self.plotLayout.addWidget(self.simplePlotCanvas)
        self.integratedPlotLayout.addWidget(self.integratedPlotCanvas)
        self.simplePlotAx = self.simplePlotCanvas.figure.subplots()
        self.integratedPlotAx = self.integratedPlotCanvas.figure.subplots()
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
        self.abortTempThread = False
        self.measurementCount = 0
        self.selectedResults = []
        self.offset = None
        self.estimatedGrating = None

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
        self.useSavedCurrentButton.clicked.connect(self.useSavedCurrent)
        self.temperatureSpinBox.valueChanged.connect(self.setTargetTemp)
        self.saveMeasurementButton.clicked.connect(self.saveCurrentMeasurement)
        self.savePlotButton.clicked.connect(self.saveCurrentPlot)
        self.correctDarkCheckBox.stateChanged.connect(self.showElectricDarkChanged)
        self.correctNonlinearCheckBox.stateChanged.connect(self.showNonlinearityChanged)
        self.measurementComplete.connect(self.onMeasurementComplete)
        self.allMeasurementsComplete.connect(self.onAllMeasurementsComplete)
        self.sortButton.clicked.connect(self.sortPending)
        # setup functions
        self.loadSettings()
        self.refreshComports()
        self.refreshSpectrometers()

        # finally, run the application
        self.show()

    def setTargetTemp(self,value):
        if self.spectrometer:
            self.spectrometer.features['thermo_electric'][0].set_temperature_setpoint_degrees_celsius(value)

    def updateTemp(self):
        while not self.abortTempThread:
            try:
                if self.spectrometer:
                    self.temperatureLabel.setText(f"{self.spectrometer.features['thermo_electric'][0].read_temperature_degrees_celsius()}°C")
                else:
                    self.temperatureLabel.setText("not connected")
                time.sleep(1)
            except Exception as e:
                print(e)

    def useSavedCurrent(self):
        if self.motorControl == None:
            QMessageBox.critical(self,"Motor control not connected","Please connect the motor control")
            return
        self.motorControl.manualCalibration()

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
            self.motorControl = MotorControlDummy(self,self.comLogBrowser,self.estimatedGrating,0)

    def selectFolder(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec():
            self.outputEdit.setText(dialog.directory().absolutePath())
    
    def updateEstimatedTime(self):
        seconds = 0
        prev = None
        for m in self.pendingMeasurements:
            if prev != None:
                seconds+=abs(prev.wavelength - m.wavelength)/2.5 #Motor does ~2.5nm/s
            seconds+= m.integrationtime * m.average
            prev = m
        dt = timedelta(seconds = int(seconds))
        self.estTimeLabel.setText(f"Estimated time: {dt}")

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
            self.abortTempThread = False
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
            self.simplePlotAx.figure.savefig(filename)

    def cleanupSpectrometer(self):
        self.abortTempThread = True
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
            self.motorControl = MotorControl(self,self.currentPort,self.comLogBrowser,self.estimatedGrating)
        except Exception as e:
            QMessageBox.critical(self,"failed intitializing:",str(e))

    def sortPending(self):
        self.pendingMeasurements.sort(key=lambda x:x.wavelength)
        self.measurementList.clear()
        self.measurementList.addItems([str(m) for m in self.pendingMeasurements])
        self.updateEstimatedTime()

    def addSingle(self):
        c = MeasurementDummy if spectrometerDummy else Measurement
        self.pendingMeasurements.append(c(self.integrationSpinBox.value(),self.fromSpinBox.value(),self.averageSpinBox.value()))
        self.sortPending()
    
    def addRange(self):
        c = MeasurementDummy if spectrometerDummy else Measurement
        for x in np.arange(self.fromSpinBox.value(),self.toSpinBox.value()+self.stepSpinBox.value(),self.stepSpinBox.value()):
            self.pendingMeasurements.append(c(self.integrationSpinBox.value(),x,self.averageSpinBox.value()))
        self.sortPending()
    
    def removeMeasurement(self):
        currentRow= self.measurementList.currentRow()
        if self.currentMeasurement and currentRow >=0:
            self.measurementList.takeItem(currentRow)
            self.pendingMeasurements.pop(currentRow)
        self.updateEstimatedTime()

    def showElectricDarkChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.correctDarkCounts = bool(value)

    def showNonlinearityChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.correctNonlinearity = bool(value)

    def showWavelengthChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.wavelength = value
            self.measurementList.item(self.measurementList.currentRow()).setText(f"{self.currentMeasurement.wavelength}nm")
        self.updateEstimatedTime()

    def showAverageChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.average = value
        self.updateEstimatedTime()

    def showIntegrationChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.integrationtime = value
        self.updateEstimatedTime()
    
    def resultChanged(self):
        selectedIndices = self.resultsList.selectionModel().selectedIndexes()
        self.selectedResults = [self.completedMeasurements[i.row()] for i in selectedIndices]
        if len(self.selectedResults)==1:
            tmp = self.selectedResults[0]
            self.resultInfoLabel.setText(tmp.getHeader()+f"\n\nTotal intensity\t\t\t{tmp.integratedIntensity:.2f}")
        else:
            self.resultInfoLabel.setText("Select a single measurement to display its properties")
        self.simplePlotAx.clear()
        self.simplePlotAx.set_ylabel("Intensity")
        self.simplePlotAx.set_xlabel("Wavelength [nm]")
        self.integratedPlotAx.clear()
        self.integratedPlotAx.set_ylabel("Integrated Intensity")
        self.integratedPlotAx.set_xlabel("Wavelength [nm]")
        tmp = [(m.wavelength,m.integratedIntensity) for m in self.selectedResults]
        if tmp:
            tmp = np.array(sorted(tmp,key= lambda k:k[0]))
            self.integratedPlotAx.plot(tmp[...,0],tmp[...,1],marker = "o")
        for m in self.selectedResults:
            self.simplePlotAx.plot(m.wavelengths,m.intensities,label=str(m.wavelength))
        self.simplePlotAx.grid()
        self.integratedPlotAx.grid()
        if self.selectedResults:
            self.simplePlotAx.legend()
        self.simplePlotAx.figure.canvas.draw()
        self.integratedPlotAx.figure.canvas.draw()
    
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
        if self.pendingMeasurements != sorted(self.pendingMeasurements,key = lambda k:k.wavelength):
            result = QMessageBox.question(self, "Confirm", "Start with unsorted measurements?",QMessageBox.Yes|QMessageBox.No)
            if result == QMessageBox.No:
                return
        self.sortPending()
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
        self.settings.setValue("offset",self.offsetSpinBox.value())
        if self.motorControl != None:
            self.settings.setValue("grating",self.motorControl.estimatedGrating)
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
        self.loadSpinBox("offset",self.offsetSpinBox)
        self.loadText("dir",self.outputEdit)
        self.loadText("filename",self.fileEdit)
        self.loadCheckBox("autosave",self.saveCheckBox)
        self.estimatedGrating = int(self.settings.value("grating") if self.settings.value("grating") else 0)
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
            widget.setCheckState(int(tmp))
        
app = QApplication(sys.argv)
window = Ui()
app.aboutToQuit.connect(window.closing)
sys.exit(app.exec_())