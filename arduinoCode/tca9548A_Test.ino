#include <Wire.h>
#include <Adafruit_INA219.h>

#define TCAADDR 0x70

/* Assign a unique ID to this sensor at the same time */
Adafruit_INA219 ina219_0;
Adafruit_INA219 ina219_1;
Adafruit_INA219 ina219_2;
Adafruit_INA219 ina219_3;
Adafruit_INA219 ina219_4;
Adafruit_INA219 ina219_5;
Adafruit_INA219 ina219_6;
Adafruit_INA219 ina219_7;


void displaySensorVals(Adafruit_INA219 *ina219, int ID)
{
  TCA9548A(ID);
  // Serial.print  ("Sensor:     "); Serial.println(ID);
  // Serial.print  ("Voltage:    "); Serial.println(ina219->getBusVoltage_V());
  Serial.print(ina219->getCurrent_mA()); Serial.print  (", ");
}

void TCA9548A(uint8_t bus)
{
  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}


void setup(void)
{
  Wire.begin();

  Serial.begin(9600);
  while (!Serial){
    delay(10);
  }
  Serial.println("TCA9548A Test");

  // initialize sensors
  TCA9548A(0);
  if(!ina219_0.begin())
  {
    Serial.println("ina219_0 not detected");
    // creates endless loop to stop program
    while(1);
  }

  TCA9548A(1);
  if(!ina219_1.begin())
  {
    Serial.println("ina219_1 not detected");
    // creates endless loop to stop program
    while(1);
  }

  TCA9548A(2);
  if(!ina219_2.begin())
  {
    Serial.println("ina219_2 not detected");
    // creates endless loop to stop program
    while(1);
  }

  TCA9548A(3);
  if(!ina219_3.begin())
  {
    Serial.println("ina219_3 not detected");
    // creates endless loop to stop program
    while(1);
  }

  TCA9548A(4);
  if(!ina219_4.begin())
  {
    Serial.println("ina219_4 not detected");
    // creates endless loop to stop program
    while(1);
  }

  TCA9548A(5);
  if(!ina219_5.begin())
  {
    Serial.println("ina219_5 not detected");
    // creates endless loop to stop program
    while(1);
  }

  TCA9548A(6);
  if(!ina219_6.begin())
  {
    Serial.println("ina219_6 not detected");
    // creates endless loop to stop program
    while(1);
  }

  TCA9548A(7);
  if(!ina219_7.begin())
  {
    Serial.println("ina219_7 not detected");
    // creates endless loop to stop program
    while(1);
  }
  Serial.println("");
  Serial.println("setup completed");
}

void loop(void)
{
  displaySensorVals(&ina219_0, 0);
  displaySensorVals(&ina219_1, 1);
  displaySensorVals(&ina219_2, 2);
  displaySensorVals(&ina219_3, 3);
  displaySensorVals(&ina219_4, 4);
  displaySensorVals(&ina219_5, 5);
  displaySensorVals(&ina219_6, 6);
  displaySensorVals(&ina219_7, 7);

  Serial.println("");
}