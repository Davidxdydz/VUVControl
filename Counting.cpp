
/*
 * Author: M Schwarz
 * Date: Tue 18 Jun 10:10:11 CEST 2019
 * 
 */

#include "Counting.h"

#include "Measurement.h"

Counting::Counting()
    : Measurement()
{
    done = false;   //no valid data until the first measurement finished
}

Couning::~Counting(){

}

void start(){
    done = false;

    //call some internal thread to run ...
    


    
}

bool isDone(){
    return done;    // currently I just handle the done check with
                    // this variable. Should be fine, as it is only 
                    // read from outside, i.e. thread-save
}

