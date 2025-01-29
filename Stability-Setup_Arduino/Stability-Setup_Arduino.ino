
// main.ino
// version 1.2

#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

#include "include/sensor.h"
#include "include/serial_com.h"
#include "include/helper.h"
#include "include/measurement.h"

// Global variables
float val1;
float val2;
int val3;
int val4;
int val5;

bool TCA9548Connected = false;
bool SensorsConnected = false;
serialCommResult messageResult = serialCommResult::NONE;

// const byte num_chars = 32;
char received_chars[num_chars];
char temp_chars[num_chars]; // temporary array for use when parsing
char mode_from_pc[num_chars] = {0};

// Perturb and Observe Variables
float Vset[8] = {0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6};
volatile bool pno_done = true;
float voltage_starting_pno = 0.0;
float voltage_step_size_pno = 0.000;
int measurement_delay_pno = 0;
int measurements_per_step_pno = 0;
unsigned long measurement_time_mins = 0;

// Scan Variables
volatile bool scan_done = true;
float avgVolt[8];
float avgCurr[8];
int volt_Step_Count = 0;
float voltage_val = 0;
uint16_t dac_val = 0;
float voltage_Range_Scan = 0.0;
float voltage_Step_Size_Scan = 0.000;
int measurements_Per_Step_Scan = 0;
int measurement_Rate_Scan = 0;
int light_Status = 0;

// Constant Voltage Variables
volatile bool constant_voltage_done = true;
float constant_voltage = 0.0;

volatile bool measurement_running = !scan_done || !constant_voltage_done || !pno_done;

void setup(void)
{
    // Pins setup
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(10, OUTPUT);
    pinMode(11, OUTPUT);
    pinMode(12, OUTPUT);
    digitalWrite(10, HIGH);
    digitalWrite(11, HIGH);
    digitalWrite(12, HIGH);

    // System setup
    Wire.begin();
    Serial.begin(115200);
    recvWithLineTermination();
    while (!Serial)
    {
        delay(10);
    }
    Serial.println("ArduinoAuto8Pixels Test");

    // Initialize sensors
    for (uint8_t ID = 0; ID < 8; ID++)
    {
        setupSensor_INA219(&allINA219[ID], ID);
    }

    for (uint8_t ID = 0; ID < 8; ID++)
    {
        setupSensor_Dac(&allDAC[ID], ID);
    }

    Serial.println("");
    Serial.println("Arduino Ready");
}
//     // System setup
//     Wire.begin();
//     Serial.begin(115200);
//     // recvWithStartEndMarkers();
//     while (!Serial) { ; } // Wait for serial port to connect.
//     Serial.println("Stability-Setup_Arduino Version: 1.2");

//     TCA9548Connected = getTCA9548Connected();
//     Serial.println(getTCA9548Connected());
//     if (TCA9548Connected)
//     {
//         Serial.println("TCA9548 Connected");
//         // Initialize sensors
//         for (uint8_t ID = 0; ID < 8; ID++)
//         {
//             Serial.println("Setting up MCP4725 with ID " + String(ID));
//             setupSensor_Dac(&allDAC[ID], ID);
//         }

//         for (uint8_t ID = 0; ID < 8; ID++)
//         {
//             Serial.println("Setting up INA219 with ID " + String(ID));
//             setupSensor_INA219(&allINA219[ID], ID);
//         }

//         // Serial.println("");
//         // Serial.println("Setup Successful");
//         SensorsConnected = true;
//     }
//     else
//     {
//         Serial.println("TCA9548 Connection Failure");
//         Serial.println("Entering Testing Mode");
//     }

//     Serial.println("Arduino Ready");
// }

void loop(void)
{
    if (TCA9548Connected && SensorsConnected)
    {
        mainLoop();
    }
    else
    {
        messageResult = recvWithLineTermination();
        if (messageResult == serialCommResult::START)
        {
            Serial.print("Measurement Started: ");
            Serial.println(mode_from_pc);

            bool run = true;
            while (run) {
                Serial.print(millis());
                Serial.println(",10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10");
                delay(1000);
            }
        }
    }
}

void mainLoop()
{
    zero();
    messageResult = recvWithLineTermination();
    if (messageResult == serialCommResult::START)
    {
        zero();

        String mode = String(mode_from_pc);
        Serial.println("Measurement Started");

        if (mode.equals("scan"))
        {
            scan_done = false;
        }
        else if (mode.equals("PnO"))
        {
            pno_done = false;
        }
        else if (mode.equals("constantVoltage"))
        {
            constant_voltage_done = false;
        }
    }

    if (!scan_done)
    {
        voltage_Range_Scan = val1;
        voltage_Step_Size_Scan = val2;
        measurements_Per_Step_Scan = val3;
        measurement_Rate_Scan = val4;
        light_Status = val5;
        light_control(light_Status);

        scan("backward");
        scan("forward");
        scan_done = true;
        Serial.println("Done!");
    }
    else if (!pno_done)
    {
        Serial.println("Perturb and Observe");

        voltage_starting_pno = val1;
        voltage_step_size_pno = val2;
        measurements_per_step_pno = val3;
        measurement_delay_pno = val4;
        measurement_time_mins = val5;

        perturb_and_observe_classic();
        pno_done = true;
        Serial.println("Done!");
    }
    else if (!constant_voltage_done)
    {
        Serial.println("Constant Voltage");

        constant_voltage = val1;
        measurements_Per_Step_Scan = val3;
        set_constant_voltage();
        constant_voltage_done = true;
        Serial.println("Done!");
    }
}