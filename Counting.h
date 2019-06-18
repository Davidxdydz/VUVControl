
/*
 * Author: M Schwarz
 * Date: Tue 18 Jun 10:10:11 CEST 2019
 *
 * Concrete class for measuring counts in a certain time window.
 * The connection to the physical counter module will be implemented, 
 * when one is found...
 * This class is derived from the abstract base class for all measure-
 * ments (Measurement). Therefore, here the start() and isDone() methods
 * are implemented.
 *
 *
 */

#ifndef COUNTING_H
#define COUNTING_H

#include "Measurement.h"

class Counting : public Measurement{
public:
    Conting();  //will likely get some initialization information
                // like measuring time, ...
    virtual ~Counting();

    virtual void start();

    virtual bool isDone(); 
    
private:
    bool done;  //this variable will be set to false when the counting 
                //starts (start() called).
                //it will be set to true again, after the counting timer
                //is over and the measurement results are retrieved
                //from the physical counter module
};

#endif //CONTING_H





