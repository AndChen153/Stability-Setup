// sensor.h
#ifndef SENSOR_H
#define SENSOR_H

#include <Arduino.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

extern Adafruit_INA219 ina219_0;
extern Adafruit_INA219 ina219_1;
extern Adafruit_INA219 ina219_2;
extern Adafruit_INA219 ina219_3;
extern Adafruit_INA219 ina219_4;
extern Adafruit_INA219 ina219_5;
extern Adafruit_INA219 ina219_6;
extern Adafruit_INA219 ina219_7;
extern Adafruit_INA219 allINA219[];

extern Adafruit_MCP4725 dac_0;
extern Adafruit_MCP4725 dac_1;
extern Adafruit_MCP4725 dac_2;
extern Adafruit_MCP4725 dac_3;
extern Adafruit_MCP4725 dac_4;
extern Adafruit_MCP4725 dac_5;
extern Adafruit_MCP4725 dac_6;
extern Adafruit_MCP4725 dac_7;
extern Adafruit_MCP4725 allDAC[];

extern float shunt_voltage;
extern float bus_voltage;
extern float current_mA;
extern float load_voltage;
extern float power_mW;
extern float current_mA_Flipped;

void setupSensor_INA219(Adafruit_INA219 *ina219, uint8_t ID);
void setupSensor_Dac(Adafruit_MCP4725 *dac, uint8_t ID);
void TCA9548A_INA219(uint8_t bus);
void TCA9548A_MCP475(uint8_t bus);
void getINA129(Adafruit_INA219 *ina219, uint8_t ID);
void setVoltage(Adafruit_MCP4725 *dac, float voltage_val, uint8_t ID);
void zero();
uint16_t convert_to_12bit(float val);

#endif
