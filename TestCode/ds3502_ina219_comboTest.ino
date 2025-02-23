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
        Serial.println("Failed to find ina219_A chip");
        while (1)
        {
            delay(10);
        }
    }
    if (!ds3502.begin())
    {
        Serial.println("Couldn't find DS3502 chip");
        while (1)
            ;
    }
    ina219_A.setCalibration_16V_400mA();

    Serial.println("Measuring voltage and current with ina219_A ...");
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

    Serial.print("Bus Voltage:  ");
    Serial.print(busvoltage_A);
    Serial.println(" V");

    Serial.print("Current:       ");
    Serial.print(current_mA_A);
    Serial.println(" mA");

    Serial.print("Resistance:    ");
    Serial.print((wiper_value / current_mA_A) * 1000);
    Serial.println("");

    Serial.print("Resistor Value: ");
    Serial.print(resistorVal);
    Serial.println(" ohms");

    // Serial.print(wiper_value);
    // Serial.println(" V");
    delay(500);
    Serial.println("");
    Serial.println("");
    // }
}