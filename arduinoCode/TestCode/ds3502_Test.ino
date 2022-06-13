#include <Adafruit_DS3502.h>

Adafruit_DS3502 ds3502 = Adafruit_DS3502();
/* For this example, make the following connections:
 * DS3502 RH to 5V
 * DS3502 RL to GND
 * DS3502 RW to the pin specified by WIPER_VALUE_PIN
 */

#define WIPER_VALUE_PIN A0
uint32_t counter;

void setup()
{
    Serial.begin(9600);
    // Wait until serial port is opened
    while (!Serial)
    {
        delay(1);
    }

    Serial.println("Adafruit DS3502 Test");

    if (!ds3502.begin())
    {
        Serial.println("Couldn't find DS3502 chip");
        while (1)
            ;
    }
    Serial.println("Found DS3502 chip");
}

void loop()
{
    for (counter = 0; counter < 128; counter += 5)
    {
        ds3502.setWiper(counter);
        float wiper_value = analogRead(WIPER_VALUE_PIN);
        wiper_value *= 5.0;
        wiper_value /= 1024;
        Serial.print(wiper_value);
        Serial.println("");
        delay(500);
    }
}
// void loop()
// {
//     // uint8_t default_value = ds3502.getWiper();

//     // Serial.print("Default wiper value: ");
//     // Serial.println(default_value);

//     //   float wiper_value = analogRead(WIPER_VALUE_PIN);
//     //   wiper_value *= 5.0;                                           // input voltage
//     //   wiper_value /= 1024;
//     float wiper_value = 100;
//     ds3502.setWiper(wiper_value);
//     Serial.print((float)ds3502.getWiper() * 10.0 / 127);
//     Serial.println("K Ohms");

//     Serial.println();
//     delay(1000);
// }