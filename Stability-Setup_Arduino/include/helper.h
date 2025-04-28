// helper.h
#ifndef HELPER_H
#define HELPER_H
#include <Arduino.h>

extern const byte relayPin;

#include <Adafruit_INA219.h>
#include <Arduino.h>

void light_control(int light_status);
void displaySensorVals(Adafruit_INA219 *ina219, int ID);
void led(bool status);

#endif