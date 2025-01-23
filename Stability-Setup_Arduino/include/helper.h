// helper.h
#ifndef HELPER_H
#define HELPER_H

#include <Adafruit_INA219.h>
#include <Arduino.h>

void light_control(int light_Status);
void displaySensorVals(Adafruit_INA219 *ina219, int ID);
void led(bool status);

#endif