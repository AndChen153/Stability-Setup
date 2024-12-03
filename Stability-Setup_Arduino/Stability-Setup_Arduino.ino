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

// const byte num_chars = 32;
char received_chars[num_chars];
char temp_chars[num_chars]; // temporary array for use when parsing
char mode_from_pc[num_chars] = {0};
boolean new_data = false;

// Perturb and Observe Variables
float Vset[8] = {0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6};
boolean perturb_And_ObserveDone = true;
float voltage_starting_pno = 0.0;
float voltage_step_size_pno = 0.000;
int measurement_delay_pno = 0;
int measurements_per_step_pno = 0;
unsigned long measurement_time_mins = 0;

// Scan Variables
boolean scan_done = true;
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
boolean constant_voltage_done = true;
float constant_voltage = 0.0;

void setup(void)
{
    // System setup
    Wire.begin();
    Serial.begin(115200);
    recvWithStartEndMarkers();
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
    Serial.println("Setup completed");
}

void loop(void)
{
    zero();
    recvWithStartEndMarkers();
    if (new_data && scan_done && perturb_And_ObserveDone && constant_voltage_done)
    {
        strcpy(temp_chars, received_chars);
        parse_data();
        show_parsed_data();
        zero();

        new_data = false;
        String mode = String(mode_from_pc);

        if (mode.equals("scan"))
        {
            scan_done = false;
        }
        else if (mode.equals("PnO"))
        {
            perturb_And_ObserveDone = false;
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
    else if (!perturb_And_ObserveDone)
    {
        Serial.println("Perturb and Observe");

        voltage_starting_pno = val1;
        voltage_step_size_pno = val2;
        measurements_per_step_pno = val3;
        measurement_delay_pno = val4;
        measurement_time_mins = val5;

        perturb_and_observe_classic();
        perturb_And_ObserveDone = true;
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