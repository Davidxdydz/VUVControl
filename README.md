# Introduction

This Project aims to provide a program to control a VUV spectrometer enable automatic measurements and selection of wavelengths via an attached motor

## Contents

motor control: Arduino code for controlling the stepper motor
GUI: Python code to run on the measurment laptop/raspberry and connect to the motor control and spectrometer, provides a hopefully easy to use user interface

## State

The program can already be used to take measurements, but is lacking some error handling etc.
IF you want to use it at this early state, don't dismiss messageboxes :)
Runs on windows and linux (tested on raspbian buster), and *maybe* on mac
At the moment there is a TODO list in every folder as opening issues in a mostly single person project is overcomplicated

## Dependencies

Installation assuming *pip* uses python3, else try *pip3*

Python >=3.7, might work with python3.6

seabreeze api for the spectrometer
matplotlib for plots
pyQt 5 for the application itself
pyserial for commumication with the arduino
```bash
pip install seabreeze
seabreeze_os_setup
pip install matplotlib
pip install pyQt5
pip install pyserial
```

## Running the GUI
just launch spectrometer.py,
or to get more error/debug messages open in terminal:
```bash
python3 spectrometer.py
```