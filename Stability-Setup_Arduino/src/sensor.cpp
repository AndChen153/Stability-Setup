// sensor.cpp
#include "../include/sensor.h"
#include <Wire.h>

// Sensor instances
Adafruit_INA219 ina219_0;
Adafruit_INA219 ina219_1;
Adafruit_INA219 ina219_2;
Adafruit_INA219 ina219_3;
Adafruit_INA219 ina219_4;
Adafruit_INA219 ina219_5;
Adafruit_INA219 ina219_6;
Adafruit_INA219 ina219_7;
Adafruit_INA219 allINA219[] = {ina219_0, ina219_1, ina219_2, ina219_3, ina219_4, ina219_5, ina219_6, ina219_7};

Adafruit_MCP4725 dac_0;
Adafruit_MCP4725 dac_1;
Adafruit_MCP4725 dac_2;
Adafruit_MCP4725 dac_3;
Adafruit_MCP4725 dac_4;
Adafruit_MCP4725 dac_5;
Adafruit_MCP4725 dac_6;
Adafruit_MCP4725 dac_7;
Adafruit_MCP4725 allDAC[] = {dac_0, dac_1, dac_2, dac_3, dac_4, dac_5, dac_6, dac_7};

// Global sensor variables
float shunt_voltage;
float bus_voltage;
float current_mA;
float load_voltage;
float power_mW;
float current_mA_Flipped;

void setupSensor_INA219(Adafruit_INA219 *ina219, uint8_t ID)
{
    TCA9548A_INA219(ID);
    if (!ina219->begin())
    {
        Serial.print("ina219_");
        Serial.print(ID);
        Serial.print(" not detected");
        while (1)
            ;
    }
    ina219->setCalibration_16V_400mA();
}

void setupSensor_Dac(Adafruit_MCP4725 *dac, uint8_t ID)
{
    TCA9548A_MCP475(ID);
    if (!dac->begin())
    {
        Serial.print("dac_");
        Serial.print(ID);
        Serial.print(" not detected");
        while (1)
            ;
    }
}

void TCA9548A_INA219(uint8_t bus)
{
    Wire.beginTransmission(0x70); // TCA9548A_INA219 address is 0x70
    Wire.write(1 << bus);         // send byte to select bus
    Wire.endTransmission();
}

void TCA9548A_MCP475(uint8_t bus)
{
    Wire.beginTransmission(0x71); // TCA9548A_MCP475 address is 0x71
    Wire.write(1 << bus);         // send byte to select bus
    Wire.endTransmission();
}

void getINA129(Adafruit_INA219 *ina219, uint8_t ID)
{
    TCA9548A_INA219(ID);
    shunt_voltage = ina219->getShuntVoltage_mV();
    bus_voltage = ina219->getBusVoltage_V();
    current_mA = ina219->getCurrent_mA();
    power_mW = ina219->getPower_mW();
    current_mA_Flipped = current_mA * -1;
    load_voltage = bus_voltage + (shunt_voltage / 1000);
}

void setVoltage(Adafruit_MCP4725 *dac, float voltage_val, uint8_t ID)
{
    TCA9548A_MCP475(ID);
    dac->setVoltage(convert_to_12bit(voltage_val), false);
}

void zero()
{
    for (int ID = 0; ID < 8; ID++)
    {
        setVoltage(&allDAC[ID], 0, ID);
    }
    delay(30);
}

uint16_t convert_to_12bit(float val)
{
    if (val < 0 || val > 3.3)
    {
        return 0;
    }
    val = val * 4095.0 / 3.3;
    int bits = floor(val);
    return bits;
}
