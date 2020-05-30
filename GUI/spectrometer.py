#pip3 install seabreeze
#pip3 install PyQt5
#pip3 install pyserial
#support: david.berger@tum.de

#options: dbgm for debugging with no motor is connected
#         dbgm for debugging with no spectrometer connected
#example: python spectrometer.py dbgm dbgs

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QListWidgetItem, QProgressBar, QInputDialog, QCheckBox, QMessageBox,QFileDialog,QLineEdit, QComboBox, QPushButton, QLabel, QTextBrowser, QScrollBar, QApplication,QListWidget,QDoubleSpinBox,QSpinBox,QGroupBox,QVBoxLayout,QTabWidget
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


class TestClass:
    def __init__(self,val):
        self.val = val
    def __str__(self):
        return str(self.val)
    def __repr__(self):
        return str(self)

class Ui(QtWidgets.QMainWindow):

    # signals
    # these are used to get threadsafe UI updates
    allMeasurementsComplete = pyqtSignal()
    measurementComplete = pyqtSignal(object)
    progressCallback = pyqtSignal(object,object)

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('dependencies/mainWindow.ui', self)  # Load the layout from ui file, can be edited with Qt Designer/ Qt Creator
        
        if "dbgs" in sys.argv:
            global spectrometerDummy
            spectrometerDummy = True
            print("Debug mode: spectrometer dummy used.")
        if "dbgm" in sys.argv:
            global motorDummy
            motorDummy = True
            print("Debug mode: motorcontrol dummy used.")

        # variables

        # all widgets are defined in mainWindows.ui

        self.tabWidget = self.findChild(QTabWidget,'tabWidget')
        # config page
        self.comPortBox = self.findChild(QComboBox, 'comPortBox')
        self.specBox = self.findChild(QComboBox, 'specBox')
        self.connectArduButton = self.findChild(QPushButton, 'connectArduButton')
        self.connectSpecButton = self.findChild(QPushButton, 'connectSpecButton')
        self.specInfoLabel = self.findChild(QLabel, 'specInfoLabel')
        self.browseButton = self.findChild(QPushButton,'browseButton')
        self.outputEdit = self.findChild(QLineEdit,'outputEdit')
        self.fileEdit = self.findChild(QLineEdit,'fileEdit')
        self.saveCheckBox = self.findChild(QCheckBox,'saveCheckBox')
        self.useSavedCurrentButton = self.findChild(QPushButton,'useSavedCurrentButton')
        self.temperatureSpinBox = self.findChild(QDoubleSpinBox,'temperatureSpinBox')
        self.temperatureLabel = self.findChild(QLabel,'temperatureLabel')
        self.offsetSpinBox = self.findChild(QDoubleSpinBox,'offsetSpinBox')

        # measurement page
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
        self.addTimerButton = self.findChild(QPushButton,'addTimerButton')

        # results page
        self.resultsList = self.findChild(QListWidget,'resultsList')
        self.resultInfoLabel = self.findChild(QLabel,'resultInfoLabel')
        self.plotLayout = self.findChild(QVBoxLayout,'plotLayout')  # the plot layouts are empty placeholders for the plots
        self.integratedPlotLayout = self.findChild(QVBoxLayout,'integratedPlotLayout')
        self.simplePlotCanvas = FigureCanvas(Figure())  # Figure Canvas can't be added in Qt Designer
        self.integratedPlotCanvas = FigureCanvas(Figure())
        self.plotLayout.addWidget(self.simplePlotCanvas)
        self.integratedPlotLayout.addWidget(self.integratedPlotCanvas)
        self.simplePlotAx = self.simplePlotCanvas.figure.subplots()
        self.integratedPlotAx = self.integratedPlotCanvas.figure.subplots()
        self.saveMeasurementButton = self.findChild(QPushButton,'saveMeasurementButton')
        self.savePlotButton = self.findChild(QPushButton,'savePlotButton')
        self.correctCheckBox = self.findChild(QCheckBox,'correctCheckBox')
        self.progressBar = self.findChild(QProgressBar,'progressBar')
        self.plotTabWidget = self.findChild(QTabWidget,'plotTabWidget')
        # settings
        self.settings = QSettings("TUM", "E15Spectrometer") # don't change company or application name unless you are fine with losing your settings
        # devices and connections
        self.ports = [] # COM Ports
        self.currentPort = None
        self.devices = []   # spectrometer devices
        self.spectrometer = None
        self.currentDevice = None
        self.motorControl = None
        # measurements
        self.completedMeasurements = []
        self.currentMeasurement = None
        self.measurementCount = 0
        self.selectedResults = []
        # threads
        self.measurementThread = None
        self.abortMeasurement = False
        self.updateTempThread = None
        self.abortTempThread = False
        self.progressBarThread = None
        self.abortProgressBar = False
        
        self.offset = None  # TODO: move this into motorcontrol
        self.estimatedGrating = None # this as well

        # TODO: find a better solution
        # variables to keep track of the current state of measurement, have to be changed manually from another thread, unelegant, error-prone and maybe not even threadsafe
        self.progressTracker = None
        self.currentAverage = 0
        self.totalTime = None

        self.redrawSimplePlot = True #For only redrawing plots when needed
        self.redrawIntegratedPlot = True

        # event triggers
        # ui elements
        self.connectArduButton.clicked.connect(self.connectArduino)
        self.startButton.clicked.connect(self.startMeasuring)
        self.addSingleButton.clicked.connect(self.addSingle)
        self.addRangeButton.clicked.connect(self.addRange)
        self.wavelengthShowSpinBox.valueChanged.connect(self.onShowWavelengthChanged)
        self.averageShowSpinBox.valueChanged.connect(self.onShowAverageChanged)
        self.integrationShowSpinBox.valueChanged.connect(self.onShowIntegrationChanged)
        self.measurementList.itemSelectionChanged.connect(self.onMeasurementChanged)
        self.resultsList.itemSelectionChanged.connect(self.onSelectedResultsChanged)
        self.removeButton.clicked.connect(self.removeMeasurement)
        self.comPortBox.currentIndexChanged.connect(self.onComPortChanged)
        self.browseButton.clicked.connect(self.onSelectFolderClick)
        self.useSavedCurrentButton.clicked.connect(self.calibrateMotor)
        self.temperatureSpinBox.valueChanged.connect(self.setTargetTemp)
        self.saveMeasurementButton.clicked.connect(self.saveCurrentMeasurement)
        self.savePlotButton.clicked.connect(self.saveCurrentPlot)
        self.correctDarkCheckBox.stateChanged.connect(self.onShowElectricDarkChanged)
        self.correctNonlinearCheckBox.stateChanged.connect(self.onShowNonlinearityChanged)
        self.correctCheckBox.stateChanged.connect(self.onSelectedResultsChanged)
        self.addTimerButton.clicked.connect(self.onAddTimerClick)
        self.plotTabWidget.currentChanged.connect(self.onCurrentPlotTabChanged)

        # threadsafe ui updates
        self.measurementComplete.connect(self.onMeasurementComplete)
        self.allMeasurementsComplete.connect(self.onAllMeasurementsComplete)
        self.progressCallback.connect(self.onSetProgressText)

        # setup functions
        self.loadSettings()
        self.refreshComports()
        self.refreshSpectrometers()
        # finally, run the application
        self.showMaximized()

    def setTargetTemp(self,temp):
        """Set the target temperature of the current Spectrometer if connected

        Parameter
        ---------
        temp : float
            target temperature in °C

        """
        if self.spectrometer:
            print(temp)
            self.spectrometer.features['thermo_electric'][0].set_temperature_setpoint_degrees_celsius(temp)

    def updateTemp(self):
        """Updates the displayed temperature of the spectrometer

            meant to be run as thread

            set self.abortTempThread = True to stop
        """
        while not self.abortTempThread:
            try:
                if self.spectrometer:
                    # TODO: make this 100% thread safe
                    self.temperatureLabel.setText(f"{self.spectrometer.features['thermo_electric'][0].read_temperature_degrees_celsius()}°C")
                else:
                    self.temperatureLabel.setText("not connected")
                time.sleep(1)
            except Exception as e:
                print(e)

    def calibrateMotor(self):
        """invokes motor calibration if motor is connected
        """
        if self.motorControl == None:
            QMessageBox.critical(self,"Motor control not connected","Please connect the motor control")
            return
        self.motorControl.calibrate()

    def onAboutToQuit(self):
        self.saveSettings()
        self.cleanup()

    def onAddTimerClick(self):
        n,result = QInputDialog.getInt(self, "Add Wait Timer","Input time in seconds",60)
        if not result:
            return
        self.addPending(WaitTimer(n))

    def onComPortChanged(self, index):
        #T TODO: reconnect to new COM Port
        if index >= 0:
            self.currentPort = self.ports[index]

    def refreshComports(self):
        self.ports = serial.tools.list_ports.comports()
        self.comPortBox.addItems([port.device for port in self.ports])
        if motorDummy:
            self.motorControl = MotorControlDummy(self,self.estimatedGrating,0)

    def onSelectFolderClick(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec():
            self.outputEdit.setText(dialog.directory().absolutePath())
    
    def onCurrentPlotTabChanged(self):
        if self.plotTabWidget.currentIndex()==0 and self.redrawSimplePlot:
            self.drawSimplePlot()
        if self.plotTabWidget.currentIndex()==1 and self.redrawIntegratedPlot:
            self.drawIntegratedPlot()

    def getPending(self):
        pending = []
        for index in range(self.measurementList.count()):
            pending.append(self.measurementList.item(index).data(QtCore.Qt.UserRole))
        return pending


    def getEstimatedTime(self,currentMeasurement = None):
        """get the time remaining in pending measurements after current measurement

            Parameter
            ---------
            currentMeasurement : Measurement, default None
                remaining time is calculated only for this and following measurements
                starts at first measurement if None
            Returns
            -------
            datetime.timedelta with remaining time
        """
        pendingMeasurements = self.getPending()
        if currentMeasurement == None and pendingMeasurements:
            currentMeasurement = pendingMeasurements[0]
        if currentMeasurement not in pendingMeasurements:
            return timedelta()
        seconds = 0
        prev = None
        for m in pendingMeasurements[pendingMeasurements.index(currentMeasurement):]:
            if prev != None:
                seconds+=abs(prev.wavelength - m.wavelength)/2.5 #Motor does ~2.5nm/s
            seconds+= m.integrationtime * m.average
            if not isinstance(prev,WaitTimer):
                prev = m
        return timedelta(seconds = int(seconds))

    def updateEstimatedTimeLabel(self):
        dt = self.getEstimatedTime()
        self.estTimeLabel.setText(f"Estimated time: {dt}")

    def refreshSpectrometers(self):
        """Refreshs the spectrometer dropdown and connects to selected
        """
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
        """Saves the selected result to user specified file if only one result is selected
        """
        if len(self.selectedResults) != 1:
            QMessageBox.critical(self,"Can't save","Select a single measurement first")
            return
        filename = QFileDialog.getSaveFileName(self,"Save","","csv File (*.txt)")[0]
        if filename:
            self.selectedResults[0].save(filename)

    def saveCurrentPlot(self):
        """Saves the plot displayed in the Simple Plot tab
        """
        filename = QFileDialog.getSaveFileName(self,"Save","","picture (*.png")[0]
        if filename:
            if self.plotTabWidget.currentIndex()==1:
                self.integratedPlotAx.figure.savefig(filename)
            else:
                self.simplePlotAx.figure.savefig(filename)

    def cleanupSpectrometer(self):
        self.abortTempThread = True
        if self.currentDevice and self.currentDevice.is_open:
            self.spectrometer.close()

    def cleanup(self):
        del self.motorControl
        self.cleanupSpectrometer()

    def connectArduino(self):
        if not self.ports:
            QMessageBox.critical(self, "nothing connected","please connect the motor control")
            return
        self.currentPort = self.ports[self.comPortBox.currentIndex()]
        try:
            self.motorControl = MotorControl(self,self.currentPort,self.estimatedGrating)
            self.connectArduButton.setText("Connected")
        except Exception as e:
            QMessageBox.critical(self,"failed intitializing:",str(e))        

    def addPending(self,measurement):
        item = QListWidgetItem(str(measurement))
        item.setData(QtCore.Qt.UserRole,measurement)
        self.measurementList.addItem(item)
        self.updateEstimatedTimeLabel()


    def addSingle(self):
        """Adds a single measurement to pending measurements with at values specified in the ui elements
        """
        c = MeasurementDummy if spectrometerDummy else Measurement
        self.addPending(c(self.integrationSpinBox.value(),self.fromSpinBox.value(),self.averageSpinBox.value()))
    
    def addRange(self):
        """Adds a range of measurements at values specified in the ui elements
        """
        c = MeasurementDummy if spectrometerDummy else Measurement
        for x in np.arange(self.fromSpinBox.value(),self.toSpinBox.value()+self.stepSpinBox.value(),self.stepSpinBox.value()):
            self.addPending(c(self.integrationSpinBox.value(),x,self.averageSpinBox.value()))
    
    def removeMeasurement(self):
        currentRow= self.measurementList.currentRow()
        if self.currentMeasurement and currentRow >=0:
            self.measurementList.takeItem(currentRow)
        self.updateEstimatedTimeLabel()

    def onShowElectricDarkChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.correctDarkCounts = bool(value)

    def onShowNonlinearityChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.correctNonlinearity = bool(value)

    def onShowWavelengthChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.wavelength = value
            self.measurementList.item(self.measurementList.currentRow()).setText(f"{self.currentMeasurement}")
        self.updateEstimatedTimeLabel()

    def onShowAverageChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.average = value
        self.updateEstimatedTimeLabel()

    def onShowIntegrationChanged(self,value):
        if self.currentMeasurement:
            self.currentMeasurement.integrationtime = value
        self.measurementList.item(self.measurementList.currentRow()).setText(f"{self.currentMeasurement}")
        self.updateEstimatedTimeLabel()

    def drawSimplePlot(self):
        self.simplePlotAx.clear()
        self.simplePlotAx.set_ylabel("Intensity")
        self.simplePlotAx.set_xlabel("Wavelength [nm]")
        self.simplePlotAx.grid()
        for m in self.selectedResults:
            if isinstance(m,WaitTimer):
                continue
            if self.correctCheckBox.checkState()!=0 and m.darkLevel != None:
                self.simplePlotAx.plot(m.correctedWavelengths,m.correctedIntensities,label=f"{m.wavelength}nm, {m.average}x{m.integrationtime}s")
            else:
                self.simplePlotAx.plot(m.wavelengths,m.intensities,label=f"{m.wavelength}nm, {m.average}x{m.integrationtime}s")
        if 1<len(self.selectedResults)<15:
            self.simplePlotAx.legend()
        self.simplePlotAx.figure.canvas.draw()
        self.redrawSimplePlot = False

    def drawIntegratedPlot(self):
        self.integratedPlotAx.clear()
        self.integratedPlotAx.set_ylabel("Integrated Intensity")
        self.integratedPlotAx.set_xlabel("Wavelength [nm]")
        self.integratedPlotAx.grid()
        if self.correctCheckBox.checkState() != 0:
            tmp = [(m.wavelength,m.correctedIntegratedIntensity if m.darkLevel else m.integratedIntensity) for m in self.selectedResults if not isinstance(m,WaitTimer)]
        else:
            tmp = [(m.wavelength,m.integratedIntensity) for m in self.selectedResults if not isinstance(m,WaitTimer)]
        if tmp:
            tmp = np.array(sorted(tmp,key= lambda k:k[0]))
            self.integratedPlotAx.plot(tmp[...,0],tmp[...,1],marker = "o")
        self.integratedPlotAx.figure.canvas.draw()
        self.redrawIntegratedPlot = False

    def onSelectedResultsChanged(self):
        """Updates the plot info and plots the selected results
        """
        selectedIndices = self.resultsList.selectionModel().selectedIndexes()
        self.selectedResults = [self.completedMeasurements[i.row()] for i in selectedIndices]
        self.redrawSimplePlot = True
        self.redrawIntegratedPlot = True
        if len(self.selectedResults)==1:
            tmp = self.selectedResults[0]
            self.resultInfoLabel.setText(tmp.getInfoText())
        else:
            self.resultInfoLabel.setText("Select a single measurement to display its properties")

        if self.plotTabWidget.currentIndex()==0:
            self.drawSimplePlot()
        if self.plotTabWidget.currentIndex()==1:
            self.drawIntegratedPlot()
    
    def onMeasurementChanged(self):
        """sets the ui elements to the values of the selected pending measurement
        """
        currentItem = self.measurementList.currentItem()
        if currentItem ==None:
            self.currentMeasurement = None
            return
        self.currentMeasurement = currentItem.data(QtCore.Qt.UserRole)
        if isinstance(self.currentMeasurement,WaitTimer):
            self.averageShowSpinBox.setEnabled(False)
            self.wavelengthShowSpinBox.setEnabled(False)
            self.correctDarkCheckBox.setEnabled(False)
            self.correctNonlinearCheckBox.setEnabled(False)
            self.integrationShowSpinBox.setMaximum(86000)
            self.integrationShowSpinBox.setValue(self.currentMeasurement.integrationtime)
        else:
            self.averageShowSpinBox.setEnabled(True)
            self.wavelengthShowSpinBox.setEnabled(True)
            self.correctDarkCheckBox.setEnabled(True)
            self.correctNonlinearCheckBox.setEnabled(True)
            self.integrationShowSpinBox.setValue(self.currentMeasurement.integrationtime)
            self.integrationShowSpinBox.setMaximum(60)
        self.averageShowSpinBox.setValue(self.currentMeasurement.average)
        self.wavelengthShowSpinBox.setValue(self.currentMeasurement.wavelength)
        self.correctDarkCheckBox.setCheckState(self.currentMeasurement.correctDarkCounts*2)
        self.correctNonlinearCheckBox.setCheckState(self.currentMeasurement.correctNonlinearity*2)


    def onMeasurementComplete(self,measurement):
        """gets called when a single measurement completes and saves it if saveCheckBox is checked
        """
        self.measurementList.takeItem(0)
        self.completedMeasurements.append(measurement)
        self.resultsList.addItem(str(measurement))
        self.updateEstimatedTimeLabel()
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
        """reenables the ui elements
        """
        self.abortProgressBar = True
        self.progressCallback.emit("Done!",10000)
        self.measurementsGroupBox.setEnabled(True)
        self.addGroupBox.setEnabled(True)
        self.infoGroupBox.setEnabled(True)
        self.startButton.setText("Start Measurement")

    def onSetProgressText(self,text,value):
        """Call self.progressCallback.emit(text,value) for threadsafety
        """
        self.progressBar.setFormat(text)
        self.progressBar.setValue(value)

    def updateProgressBar(self):
        """Updates the progress bar 20 times per second

            meant to be run as thread

            set self.abortProgressBar = True to stop
        """
        while not self.abortProgressBar:
            time.sleep(0.05)
            cur = self.progressTracker
            if cur == None or cur.startTime == None:
                continue
            remaining = self.getEstimatedTime(cur)-(datetime.now()-cur.startTime)
            percent = min(max(int(10000-remaining/self.totalTime*10000),0),10000)
            remaining = timedelta(seconds = int(remaining.seconds))
            self.progressCallback.emit(f"{remaining} remaining, {cur.wavelength}nm: {cur.integrationtime}s {self.currentAverage+1}/{cur.average}",percent)
        else:
            self.progressCallback.emit(f"Done!",10000)

    def measureAll(self):
        """Attempts all pending measurements

            meant to be run as thread

            set self.abortMeasurement = True to stop after current measurement completes
        """
        self.totalTime = self.getEstimatedTime() # also updates pending measurements
        for cur in self.getPending():   # make a copy that doesn't change while running
            self.progressTracker = cur
            if self.abortMeasurement:
                break
            try:
                cur.measure(self.spectrometer,self.motorControl,self)
            except Exception as e:
                print("Measurement failed:",e)
            if cur.completed:
                self.measurementComplete.emit(cur)
        self.allMeasurementsComplete.emit()

    def startMeasuring(self):
        """disables some ui elements and starts measurement threads
        """
        if self.measurementThread and self.measurementThread.is_alive():
            self.abortMeasurement = True
            self.abortProgressBar = True
            return
        if self.motorControl == None:
            QMessageBox.critical(self,"Can't Start","Motor control not connected!")
            return
        if self.spectrometer == None and not spectrometerDummy:
            QMessageBox.critical(self,"Can't Start","Spectrometer not connected!")
            return
        if self.measurementList.count()<1:
            QMessageBox.information(self,"Can't Start","No measurements configured!")
            return
        self.abortMeasurement = False
        self.abortProgressBar = False
        self.measurementsGroupBox.setEnabled(False)
        self.addGroupBox.setEnabled(False)
        self.infoGroupBox.setEnabled(False)
        self.startButton.setText("Stop Measurement")
        self.tabWidget.setCurrentIndex(1)
        self.measurementThread = threading.Thread(target=self.measureAll, daemon=True)
        self.measurementThread.start()
        self.progressBarThread = threading.Thread(target=self.updateProgressBar,daemon=True)
        self.progressBarThread.start()
        
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
        self.settings.setValue("correct",self.correctCheckBox.checkState())
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
        self.loadCheckBox("correct",self.correctCheckBox)
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
app.aboutToQuit.connect(window.onAboutToQuit)
sys.exit(app.exec_())