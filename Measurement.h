
/*
 * Author: M Schwarz
 * Date: Mon 17 Jun 17:45:51 CEST 2019
 *
 * Abstract base class for all kinds of Measurement connected
 * to the Optics setup
 *
 * Idea: Every Concrete Measurement class (Counting for PMT/single photon,
 * OceanOptics for Spectrometer, ...) is derived from this abstract class.
 * This means, that there is a common base of methods for the interface
 * between the steppermotor/wavelength selecting side and the measuring side.
 * I.e. the steppermotor calls start for a Measurement (let's say it's 
 * Counting, but the steppermotor doesn't have to know). The Counting now
 * is informed, that the wavelength is selected and starts the physical 
 * counter module. If the counting is done, the return value of the
 * method isDone() gets true --> the steppermotor now knows, that the 
 * measurement is done and selects the next wavelength. 
 */

#ifndef MEASUREMENT_H
#define MEASUREMENT_H

/*public abstract*/ class Measurement{

public:
    Measurement();
    virtual ~Measurement();

    void start() = 0;   //method to start a measurement. Only call it, if
                    //everything is set up (e.g. the correct wavelength
                    // is set at the monochromator).
    
    bool isDone() = 0;  //measurements should stop by themselves.
                    //with this method, you should be able to poll,
                    //if the Measurement is over (true) or still 
                    //running (false)



};

#endif //MEASUREMENT_H

