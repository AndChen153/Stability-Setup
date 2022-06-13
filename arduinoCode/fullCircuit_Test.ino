#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac_A;
Adafruit_INA219 ina219_A(0x41);

uint16_t input;
int temp;
// float dacVoltsOut;

void setup()
{
    Serial.begin(115200);
    while (!Serial)
    {
        // will pause Zero, Leonardo, etc until serial console opens
        delay(1);
    }
    if (!ina219_A.begin())
    {
        Serial.println("Failed to find ina219_A chip");
        while (1)
        {
            delay(10);
        }
    }
    if (!dac_A.begin())
    {
        Serial.println("Failed to find dac_A chip");
        while (1)
        {
            delay(10);
        }
    }

    // dacVoltsOut = 0.8;
    ina219_A.setCalibration_16V_400mA();

    input = 3000;
}

void loop()
{
    if (Serial.available())
    {
        int volts = Serial.parseInt();
        if (volts > 0)
        {
            // Serial.println(volts);
            input = (uint16_t)volts;
        }
        else if (volts == -1)
        {
            input = 0;
        }

        // if
        // if (input > 4095 or input < 0)
        // {
        //     input = 0;
        // }
    }
    float shuntvoltage_A = 0;
    float busvoltage_A = 0;
    float current_mA_A = 0;
    float loadvoltage_A = 0;
    float power_mW_A = 0;

    // dac_A.setVoltage((uint16_t)(dacVoltsOut * 4095.0 / 3.3), false);
    dac_A.setVoltage(input, false);

    shuntvoltage_A = ina219_A.getShuntVoltage_mV();
    busvoltage_A = ina219_A.getBusVoltage_V();
    current_mA_A = ina219_A.getCurrent_mA();
    if (current_mA_A < 0)
    {
        current_mA_A = 0;
    }
    power_mW_A = ina219_A.getPower_mW();

    loadvoltage_A = busvoltage_A + (shuntvoltage_A / 1000);

    Serial.print(input);
    Serial.print(", ");
    Serial.print(current_mA_A);

    Serial.println("");
    delay(50);
}

// Serial.print("dac Voltage: ");
// Serial.print((input/4095.0) * 3.3);
// Serial.println(" V");

// Serial.print("Load Voltage:   ");
// Serial.print(loadvoltage_A);
// // Serial.print(busvoltage_A);
// // Serial.print(shuntvoltage_A);
// Serial.println(" V");

// Serial.print("Current:        ");
// Serial.print(current_mA_A);
// Serial.println(" mA");

// Serial.print("Resistance:     ");
// Serial.print((loadvoltage_A / current_mA_A));
// Serial.println("k ohms");
