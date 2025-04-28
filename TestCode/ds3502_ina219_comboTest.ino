#include <Adafruit_DS3502.h>

Adafruit_DS3502 ds3502 = Adafruit_DS3502();

#define WIPER_VALUE_PIN A0
uint32_t counter;
#include <Wire.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina219_A(0x41);
// Adafruit_INA219 ina219_B(0x41);

int count = 0;

void setup(void)
{

    Serial.begin(9600);
    while (!Serial)
    {
        // will pause Zero, Leonardo, etc until serial console opens
        delay(1);
    }

    uint32_t currentFrequency;

    if (!ina219_A.begin())
    {
        Serial.println(F("Failed to find ina219_A chip"));
        while (1)
        {
            delay(10);
        }
    }
    if (!ds3502.begin())
    {
        Serial.println(F("Couldn't find DS3502 chip"));
        while (1)
            ;
    }
    ina219_A.setCalibration_16V_400mA();

    Serial.println(F("Measuring voltage and current with ina219_A ..."));
}

void loop()
{
    // for (counter = 0; counter < 128; counter++)
    // {
    counter = 127;
    ds3502.setWiper(counter);
    float wiper_value = analogRead(WIPER_VALUE_PIN);
    wiper_value *= 5.0;
    wiper_value /= 1024;
    float resistorVal = (127 - counter) * 78.125;

    float shuntvoltage_A = 0;
    float busvoltage_A = 0;
    float current_mA_A = 0;
    float loadvoltage_A = 0;
    float power_mW_A = 0;

    shuntvoltage_A = ina219_A.getShuntVoltage_mV();
    busvoltage_A = ina219_A.getBusVoltage_V();
    current_mA_A = ina219_A.getCurrent_mA();
    power_mW_A = ina219_A.getPower_mW();
    loadvoltage_A = busvoltage_A + (shuntvoltage_A / 1000);

    Serial.print(F("Bus Voltage:  "));
    Serial.print(F(busvoltage_A));
    Serial.println(F(" V"));

    Serial.print(F("Current:       "));
    Serial.print(F(current_mA_A));
    Serial.println(F(" mA"));

    Serial.print(F("Resistance:    "));
    Serial.print(F((wiper_value / current_mA_A) * 1000);
    Serial.println(F(""));

    Serial.print(F("Resistor Value: "));
    Serial.print(F(resistorVal));
    Serial.println(F(" ohms"));

    // Serial.print(F(wiper_value));
    // Serial.println(F(" V"));
    delay(500);
    Serial.println(F(""));
    Serial.println(F(""));
    // }
}