// measurement.h
#ifndef MEASUREMENT_H
#define MEASUREMENT_H

#include <Arduino.h>
#include <math.h>


enum ScanDirection {
    SCAN_FORWARD,
    SCAN_BACKWARD
  };

void perturb_and_observe();
void perturbAndObserveClassic();
void scan(ScanDirection dir);
void setConstantVoltage();

#endif
