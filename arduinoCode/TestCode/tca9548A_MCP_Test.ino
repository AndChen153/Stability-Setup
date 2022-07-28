#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

// #define TCAADDR 0x70

/* Assign a unique ID to this sensor at the same time */

Adafruit_MCP4725 dac_0;
Adafruit_MCP4725 dac_1;
Adafruit_MCP4725 dac_2;
Adafruit_MCP4725 dac_3;
Adafruit_MCP4725 dac_4;
Adafruit_MCP4725 dac_5;
Adafruit_MCP4725 dac_6;
Adafruit_MCP4725 dac_7;
Adafruit_MCP4725 allDAC[] = {dac_0, dac_1, dac_2, dac_3, dac_4, dac_5, dac_6, dac_7};

void setupSensor_Dac(Adafruit_MCP4725 *dac, uint8_t ID)
{
  Serial.println("Test");
  TCA9548A_MCP475(ID);
  if (!dac->begin())
  {
    Serial.print("dac_");
    Serial.print(ID);
    Serial.print(" not detected");
    // creates endless loop to stop program
    while (1)
      ;
  }
  // Serial.print("INA219_"); Serial.print(ID); Serial.println(" is setup");
}

void TCA9548A_MCP475(uint8_t bus)
{
  Wire.beginTransmission(0x71); // TCA9548A address is 0x70
  Wire.write(1 << bus);         // send byte to select bus
  Wire.endTransmission();
}

// set the DAC voltage out
void setVoltage(Adafruit_MCP4725 *dac, float voltage_val, uint8_t ID)
{
  TCA9548A_MCP475(ID);
  dac->setVoltage(convert_to_12bit(voltage_val), false);
}

// convert decimal voltage value to 12 bit int to control the MCP4725
uint16_t convert_to_12bit(float val)
{
  if (val < 0 or val > 3.3)
  {
    return 0;
  }
  val = float(val) * 4095.0 / 3.3;
  int bits = floor(val);
  return bits;
}

void setup(void)
{
  Wire.begin();

  Serial.begin(115200);
  while (!Serial)
  {
    delay(10);
  }

  Serial.println("started");

  // initialize sensors
  // TCA9548A_MCP475(0);
  // if (!dac_0.begin())
  // {
  //   Serial.print("dac_");
  //   Serial.print(0);
  //   Serial.print(" not detected");
  //   // creates endless loop to stop program
  //   while (1);
  // }

  // TCA9548A_MCP475(1);
  // if(!dac_1.begin())
  // {
  //   Serial.println("ina219_2 not detected");
  //   // creates endless loop to stop program
  //   while(1);
  // }
  for (uint8_t ID = 0; ID < 8; ID++)
  {
    // Serial.println(ID);
    setupSensor_Dac(&allDAC[ID], ID);
  }

  Serial.println("");
  Serial.println("setup completed");
}

void loop(void)
{
  for (int ID = 0; ID < 8; ID++)
  {
    setVoltage(&allDAC[ID], 2, ID);
  }
}