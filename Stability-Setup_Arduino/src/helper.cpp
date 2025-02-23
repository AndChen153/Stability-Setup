// helper.cpp
#include "../include/helper.h"
#include "../include/sensor.h"
#include "../include/serial_com.h"
#include <Arduino.h>

void light_control(int light_status)
{
    if (light_status == 0)
    {
        Serial.println("Turn light off");
    }
    else if (light_status == 1)
    {
        Serial.println("Turn light on");
    }
}

void displaySensorVals(Adafruit_INA219 *ina219, int ID)
{
    Serial.println("------------------------------------");
    Serial.print("Sensor:     ");
    Serial.println(ID);
    Serial.print("Voltage:    ");
    Serial.println(ina219->getBusVoltage_V());
    Serial.print("Current:    ");
    Serial.println(ina219->getCurrent_mA());
    Serial.println("------------------------------------");
    Serial.println("");
    delay(500);
}

void led(bool status)
{
    digitalWrite(LED_BUILTIN, status ? HIGH : LOW);
}
