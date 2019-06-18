
Introduction
============

This Project aims to provide a program to control a VUV spectrometer.


My ideas of the code structure
------------------------------

I think, we can leave the steppermotor class as basically the main class,
which calls the other classes (Measurements).
This is fine, because it represents the measurement procedure:
1. set the wavelength according to user input --> turn motor
2. when the correct wavelength is reached, call the Measurement (1 ore more)
3. wait for it (or them) to be finished, then proceed with step 1.

I set up the Measurement abstract class, ideally all Measurements are derived
from this. This grants a common standard for all Measurements. 


