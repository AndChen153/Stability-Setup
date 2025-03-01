// sensor.cpp
#include "../include/sensor.h"
#include <Wire.h>

#define WIRE Wire

// Global sensor variables
Adafruit_INA219 adcDevices[NUM_ADCS] = {
    Adafruit_INA219(ADC_I2C),
    Adafruit_INA219(ADC_I2C+1),
    Adafruit_INA219(ADC_I2C+2),
    Adafruit_INA219(ADC_I2C+3),
    Adafruit_INA219(ADC_I2C+4),
    Adafruit_INA219(ADC_I2C+5),
    Adafruit_INA219(ADC_I2C+6),
    Adafruit_INA219(ADC_I2C+7)};

Adafruit_MCP4725 dacDevices[NUM_DACS];

float shunt_voltage;
float bus_voltage;
float current_mA;
float load_voltage;
float power_mW;
float current_mA_Flipped;

void setupSensor_DAC(uint8_t ID)
{
    if (!dacDevices[ID].begin(DAC_I2C + ID))
    {
        Serial.print("Failed to find MCP4725 at 0x");
        Serial.println(DAC_I2C + ID, HEX);
    }
    // else
    // {
    //     Serial.print("Found MCP4725 at 0x");
    //     Serial.println(DAC_I2C + ID, HEX);
    // }
}

void setVoltage_V(float voltage_val, uint8_t ID)
{
    dacDevices[ID].setVoltage(convert_to_12bit(voltage_val), false);
}

void zero()
{
    for (int ID = 0; ID < 8; ID++)
    {
        setVoltage_V(0, ID);
    }
    delay(30);
}

void setupSensor_ADC(uint8_t ID)
{
    if (!adcDevices[ID].begin())
    {
        Serial.print("Failed to find INA219 at 0x");
        Serial.println(ADC_I2C + ID, HEX);
    }
    // else
    // {
    //     Serial.print("Found INA219 at 0x");
    //     Serial.println(ADC_I2C + ID, HEX);
    // }
}


void getADC(uint8_t ID)
{
    shunt_voltage = adcDevices[ID].getShuntVoltage_mV();
    bus_voltage = adcDevices[ID].getBusVoltage_V();
    current_mA = adcDevices[ID].getCurrent_mA();
    power_mW = adcDevices[ID].getPower_mW();
    current_mA_Flipped = current_mA * -1;
    load_voltage = bus_voltage + (shunt_voltage / 1000);
}

float getCurrent_A(uint8_t ID)
{
    float volts = adcDevices[ID].getShuntVoltage_mV()/1000.0;
    return volts/R;
}

float get_current_flipped_A(uint8_t ID)
{
    float volts = adcDevices[ID].getShuntVoltage_mV()/1000.0;
    return -1.0*volts/R;
}

float getCurrent_mA(uint8_t ID) {
    return adcDevices[ID].getShuntVoltage_mV() / R;
}

float get_current_flipped_mA(uint8_t ID)
{
    return -1.0*adcDevices[ID].getShuntVoltage_mV() / R;
}

float get_voltage_V(uint8_t ID)
{
    return (adcDevices[ID].getBusVoltage_V()
        + (adcDevices[ID].getShuntVoltage_mV()/1000.0));
}

float getVoltage_mV(uint8_t ID)
{
    return (adcDevices[ID].getBusVoltage_V()*1000.0
    + adcDevices[ID].getShuntVoltage_mV());
}

uint16_t convert_to_12bit(float val)
{
    if (val < 0 || val > VDD)
    {
        return 0;
    }
    val = val * 4095.0 / VDD;
    int bits = floor(val);
    return bits;
}
