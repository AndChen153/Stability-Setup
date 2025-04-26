// sensor.h
#ifndef SENSOR_H
#define SENSOR_H

#define NUM_ADCS 8
#define NUM_DACS 8

#define ADC_I2C 0x40
#define DAC_I2C 0x60
#define VDD 3.3     // Supply voltage (V) for DAC conversion calculation
#define R 10

#include <Arduino.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

// Global sensor variables
extern Adafruit_INA219 adcDevices[NUM_ADCS];
extern Adafruit_MCP4725 dacDevices[NUM_DACS];
extern float shunt_voltage;
extern float bus_voltage;
extern float current_mA;
extern float load_voltage;
extern float power_mW;
extern float current_mA_Flipped;
extern bool init_success;

void setupSensor_ADC(uint8_t ID);
void setupSensor_DAC(uint8_t ID);
void getADC(uint8_t ID);
float getCurrent_A(uint8_t ID);
float get_current_flipped_A(uint8_t ID);
float getCurrent_mA(uint8_t ID);
float get_current_flipped_mA(uint8_t ID);
float get_voltage_V(uint8_t ID);
float getVoltage_mV(uint8_t ID);
void setVoltage_V(float voltage_val, uint8_t ID);
void zero();
uint16_t convert_to_12bit(float val);

#endif
