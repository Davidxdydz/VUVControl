# Introduction

This Project aims to provide a program to control a VUV spectrometer, enable automatic measurements and selection of wavelengths via an attached motor.

The code here was part of my bachelor's thesis in physics at the E15 chair at the Technical University of Munich. A more up to date copy of this code can be found at the private E15 gitlab.

## Contents

motor control: Arduino code for controlling the stepper motor  
GUI: Python code to run on the measurement laptop/raspberry and connect to the motor control and spectrometer, provides a hopefully easy to use user interface

## State

Stable (one known bug with unkown origin might crash the program at setup, while taking measurements over an extended period of time no crashes have occured so far as all critical methods are wrapped in tons of error handling)  

Runs on windows and linux (tested on raspbian buster), and *maybe* on mac  

There are a few quality of live improvements to be done, those are tagged as low priority issues at the E15 gitlab.   

The program was tested using an ocean optics (now ocean insight) QE65000 spectrometer

## Dependencies

Installation assuming *pip* uses python3, else try *pip3*

Python >=3.7, might work with python3.6

seabreeze api for the spectrometer  
matplotlib for plots  
pyQt 5 for the application itself  
pyserial for commumication with the arduino  
```bash
pip3 install seabreeze
seabreeze_os_setup
pip3 install matplotlib
pip3 install PyQt5
pip3 install pyserial
```

## Running the GUI
Execute with double click (Windows) or from the terminal
```bash
python3 spectrometer.py
```
### Launch Options
**dbgm**: emulate the motor  
**dbgs**: emulate the spectrometer, the intensities returned are random sine waves  
Example:
```bash
python3 spectrometer.py dbgm dbgs
```

##  Usage
All settings get saved between launches, so some steps can be skipped after the inital launch. Steps 3 to 6 do not have a specific order.
1. Connect spectrometer and arduino via usb
2. Click the "connect" button, wait for "connected"
3. Input the offset in nanometers of the gratings dial (should probably stay at -26.3)
4. Input the number on the gratings dial after clicking "calibrate to current wavelength"
5. Set the target temperature of the spectrometer
6. Configure your output files
7. Go to the "Create Measurements" tab and start measuring!

## Things to be aware of
- The autosave function overwrites existing files without asking
- The application needs to be restarted when spectrometer or motor (arduino) have not been connected at launch
- Aborting measurements takes some time as the current measurement is always finished first
- Sometimes the spectrometer can't keep up with cooling (espacially in a warm environment) and just gives up
- Sometimes the dark-and-dead correction does not work properly; the plots will then fall back to the raw spectrum without warning