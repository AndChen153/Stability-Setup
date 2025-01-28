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

  // Initialize the ina219_A.
  // By default the initialization will use the largest range (32V, 2A).  However
  // you can call a setCalibration function to change this range (see comments).
  if (!ina219_A.begin())
  {
    Serial.println("Failed to find ina219_A chip");
    while (1)
    {
      delay(10);
    }
  }

  // if (! ina219_B.begin()) {
  //   Serial.println("Failed to find ina219_B chip");
  //   while (1) { delay(10); }
  // }

  ina219_A.setCalibration_16V_400mA();
  // ina219_B.setCalibration_16V_400mA();
  // To use a slightly lower 32V, 1A range (higher precision on amps):
  // ina219_A.setCalibration_32V_1A();
  // Or to use a lower 16V, 400mA range (higher precision on volts and amps):
  // ina219_A.setCalibration_16V_400mA();

  Serial.println("Measuring voltage and current with ina219_A/B ...");
}

void loop(void)
{
  float shuntvoltage_A = 0;
  float busvoltage_A = 0;
  float current_mA_A = 0;
  float loadvoltage_A = 0;
  float power_mW_A = 0;

  float shuntvoltage_B = 0;
  float busvoltage_B = 0;
  float current_mA_B = 0;
  float loadvoltage_B = 0;
  float power_mW_B = 0;

  shuntvoltage_A = ina219_A.getShuntVoltage_mV();
  busvoltage_A = ina219_A.getBusVoltage_V();
  current_mA_A = ina219_A.getCurrent_mA();
  power_mW_A = ina219_A.getPower_mW();
  loadvoltage_A = busvoltage_A + (shuntvoltage_A / 1000);

  // shuntvoltage_B = ina219_B.getShuntVoltage_mV();
  // busvoltage_B = ina219_B.getBusVoltage_V();
  // current_mA_B = ina219_B.getCurrent_mA();
  // power_mW_B = ina219_B.getPower_mW();
  // loadvoltage_B = busvoltage_B + (shuntvoltage_B / 1000);

  // Serial.print("Bus Voltage:   "); Serial.print(busvoltage_A); Serial.println(" V");
  // Serial.print("Shunt Voltage: "); Serial.print(shuntvoltage_A); Serial.println(" mV");
  Serial.print("Bus Voltage:  ");
  Serial.print(busvoltage_A);
  Serial.println(" V");

  Serial.print("Current:       ");
  Serial.print(current_mA_A);
  Serial.println(" mA");

  Serial.print("Resistance:    ");
  Serial.print((busvoltage_A / current_mA_A)*1000);

  Serial.println("");
  Serial.println("");

  delay(500);
}