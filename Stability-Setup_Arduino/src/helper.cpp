// helper.cpp
#include "../include/helper.h"
#include "../include/sensor.h"
#include "../include/serial_com.h"

extern const byte relayPin;

void light_control(int light_status)
{
    if (light_status == 0)
    {
        Serial.println(F("Turn light off"));
    }
    else if (light_status == 1)
    {
        digitalWrite(relayPin, HIGH);
        Serial.println(F("Turn light on"));
    }
}

void displaySensorVals(Adafruit_INA219 *ina219, int ID)
{
    Serial.println(F("------------------------------------"));
    Serial.print(F("Sensor:     "));
    Serial.println(ID);
    Serial.print(F("Voltage:    "));
    Serial.println(ina219->getBusVoltage_V());
    Serial.print(F("Current:    "));
    Serial.println(ina219->getCurrent_mA());
    Serial.println(F("------------------------------------"));
    Serial.println(F(""));
    delay(500);
}

void led(bool status)
{
    digitalWrite(LED_BUILTIN, status ? HIGH : LOW);
}
