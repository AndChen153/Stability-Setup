// //TESTING MODE
// //TESTING MODE
// //TESTING MODE
// //TESTING MODE
// //TESTING MODE
// //TESTING MODE
// // version 1.2

// #include <EEPROM.h>
// #include <Wire.h>
// #include <Adafruit_INA219.h>
// #include <Adafruit_MCP4725.h>

// #include "include/sensor.h"
// #include "include/serial_com.h"
// #include "include/helper.h"
// #include "include/measurement.h"

// // Global variables
// float val1;
// float val2;
// int val3;
// int val4;
// int val5;

// const int idAddress = 0;
// uint32_t uniqueID;

// bool TCA9548Connected = false;
// bool SensorsConnected = false;
// serialCommResult messageResult = serialCommResult::NONE;

// // const byte num_chars = 32;
// char received_chars[num_chars];
// char temp_chars[num_chars]; // temporary array for use when parsing
// char mode_from_pc[num_chars] = {0};

// // Perturb and Observe Variables
// float vset[8] = {0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6};
// volatile bool mppt_done = true;
// float voltage_starting_mppt = 0.0;
// float voltage_step_size_mppt = 0.000;
// int measurement_delay_mppt = 0;
// int measurements_per_step_mppt = 0;
// unsigned long measurement_time_mins_mppt = 0;

// // Scan Variables
// volatile bool scan_done = true;
// float avg_volt[8];
// float avg_curr[8];
// int volt_step_count = 0;
// float voltage_val = 0;
// uint16_t dac_val = 0;
// float voltage_range_scan = 0.0;
// float voltage_step_size_scan = 0.000;
// int measurements_per_step_scan = 0;
// int measurement_rate_scan = 0;
// int light_status = 0;

// // Constant Voltage Variables
// volatile bool constant_voltage_done = true;
// float constant_voltage = 0.0;

// float fake_voltage = 0.0;
// bool fake_direction = true;

// // TODO: remove this variable
// volatile bool measurement_running = !scan_done || !constant_voltage_done || !mppt_done;

// void setup(void)
// {
//     long seed = analogRead(A0) + analogRead(A1) + analogRead(A2);
//     randomSeed(seed);

//     // // Pins setup
//     // pinMode(LED_BUILTIN, OUTPUT);
//     // pinMode(10, OUTPUT);
//     // pinMode(11, OUTPUT);
//     // pinMode(12, OUTPUT);
//     // digitalWrite(10, HIGH);
//     // digitalWrite(11, HIGH);
//     // digitalWrite(12, HIGH);

//     // System setup
//     Wire.begin();
//     Serial.begin(115200);
//     while (!Serial)
//     {
//         delay(10);
//     }

//     EEPROM.get(idAddress, uniqueID);
//     if (uniqueID == 0xFFFFFFFFUL) {
//         uint32_t high = random(0, 0x10000);  // 16 bits
//         uint32_t low  = random(0, 0x10000);  // another 16 bits
//         uniqueID = (high << 16) | low;
//         EEPROM.put(idAddress, uniqueID);
//         Serial.print("seed: ");
//         Serial.println(seed);
//         Serial.print("Generated and stored new ID: ");
//     }

//     Serial.print("HW_ID:");
//     Serial.println(uniqueID, HEX);
//     Serial.println("Arduino Ready");
// }

// void loop(void)
// {
//     messageResult = recvWithLineTermination();
//     if (messageResult == serialCommResult::START)
//     {

//         String mode = String(mode_from_pc);
//         Serial.println("Measurement Started");

//         if (mode.equals("scan"))
//         {
//             scan_done = false;
//         }
//         else if (mode.equals("PnO"))
//         {
//             mppt_done = false;
//         }
//         else if (mode.equals("constantVoltage"))
//         {
//             constant_voltage_done = false;
//         }
//     }

//     if (!scan_done)
//     {
//         while(!scan_done){
//             Serial.print("0.4410,1.2,");
//             Serial.print(fake_voltage);
//             Serial.println(",-1.4600,1.2002,-1.6400,1.1921,-1.2600,1.1961,-1.3600,1.2018,-1.5800,1.2002,-1.5000,1.1881,-1.4200,1.2001,-1.4400,1");
//             if (fake_voltage > 1.2) {
//                 fake_direction = false;
//             } else if (fake_voltage < 0) {
//                 scan_done = true;
//             }

//             if (fake_direction) {
//                 fake_voltage += 0.03;
//             } else {
//                 fake_voltage -= 0.03;
//             }

//             delay(300);
//         }
//         Serial.println("Done!");


//     }
//     else if (!mppt_done)
//     {
//         Serial.println("not Implemented");
//         mppt_done = true;
//         Serial.println("Done!");

//     }
//     else if (!constant_voltage_done)
//     {
//         Serial.println("not Implemented");
//         constant_voltage_done = true;
//     }
// }