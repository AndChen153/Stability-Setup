/**************************************************************************/
/*!
    @file     trianglewave.pde
    @author   Adafruit Industries
    @license  BSD (see license.txt)
    This example will generate a triangle wave with the MCP4725 DAC.
    This is an example sketch for the Adafruit MCP4725 breakout board
    ----> http://www.adafruit.com/products/935

    Adafruit invests time and resources providing this open source code,
    please support Adafruit and open-source hardware by purchasing
    products from Adafruit!
*/
/**************************************************************************/
#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac;
float voltageOut;

void setup(void)
{
    Serial.begin(9600);

    // For Adafruit MCP4725A1 the address is 0x62 (default) or 0x63 (ADDR pin tied to VCC)
    // For MCP4725A0 the address is 0x60 or 0x61
    // For MCP4725A2 the address is 0x64 or 0x65
    if (!dac.begin())
    {
        Serial.println(F("Failed to find dac_A chip"));
        while (1)
        {
            delay(10);
        }
    }
    voltageOut = 5.0;
    Serial.println(F("Voltage Out = "));
    Serial.print(F(2));
}

void loop(void)
{
    // uint32_t counter;
    // // Run through the full 12-bit scale for a triangle wave
    // for (counter = 0; counter < 4095; counter++)
    // {
        // dac.setVoltage(counter, false);
    //     Serial.println(F(5.0*(counter/4095.0));
    //       delay(50);
    // }
    // for (counter = 4095; counter > 0; counter--)
    // {
    //     dac.setVoltage(counter, false);
    //     Serial.println(F(5.0*(counter/4095.0));
    //       delay(50);
    // }

    dac.setVoltage(convert_to_12bit(3), false);

}

// convert decimal voltage value to 12 bit int to control the MCP4725
uint16_t convert_to_12bit(float val) {
    if (val < 0 or val > 3.3) {
        return 0;
    }
    val = float(val)*4095.0/3.3;
    int bits = floor(val);
    return bits;
}