// main.ino
// version 1.2

#include <EEPROM.h>
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
int val6;

const int idAddress = 0;
uint32_t uniqueID;

const int relayPin = 7;

// const byte num_chars = 32;
char received_chars[num_chars];
// char temp_chars[num_chars]; // temporary array for use when parsing
char mode_from_pc[MAX_MODE_LEN] = {0};

// Perturb and Observe Variables
float vset[8] = {0.0,0.0,0.0,0.0,0.0,0.0};
volatile bool mppt_done = true;
float voltage_starting_mppt = 0.0;
float voltage_step_size_mppt = 0.000;
int measurement_delay_mppt = 0;
int measurements_per_step_mppt = 0;
unsigned long measurement_time_mins_mppt = 0;

// Scan Variables
volatile bool scan_done = true;
float avg_volt[8];
float avg_curr[8];
int volt_step_count = 0;
float voltage_val = 0;
uint16_t dac_val = 0;
float voltage_range_scan = 0.0;
float voltage_step_size_scan = 0.000;
int measurements_per_step_scan = 0;
int measurement_rate_scan = 0;
int light_status = 0;

extern float area_of_collector_mppt = 0.0;


// Constant Voltage Variables
volatile bool constant_voltage_done = true;
float constant_voltage = 0.0;

volatile bool measurement_running = !scan_done || !constant_voltage_done || !mppt_done;
// TODO: implement blinking for ID
void setup(void)
{
    long seed = analogRead(A0) + analogRead(A1) + analogRead(A2);
    randomSeed(seed);

    // System setup
    Wire.begin();
    Serial.begin(115200);
    while (!Serial)
    {
        delay(10);
    }

    EEPROM.get(idAddress, uniqueID);
    if (uniqueID == 0xFFFFFFFFUL) {
        uint32_t high = random(0, 0x10000);  // 16 bits
        uint32_t low  = random(0, 0x10000);  // another 16 bits
        uniqueID = (high << 16) | low;
        EEPROM.put(idAddress, uniqueID);
        Serial.print("Generated and stored new ID: ");
    }

    Serial.print("HW_ID:");
    Serial.println(uniqueID, HEX);

    pinMode(relayPin, OUTPUT);
    digitalWrite(relayPin, LOW);

    // Initialize sensors
    for (uint8_t ID = 0; ID < 8; ID++)
    {
        setupSensor_ADC(ID);
    }

    for (uint8_t ID = 0; ID < 8; ID++)
    {
        setupSensor_DAC(ID);
    }

    Serial.println("");
    Serial.println("Arduino Ready");
}

void loop(void)
{
    zero();
    if (recvWithLineTermination() == serialCommResult::START)
    {
        zero();

        String mode = String(mode_from_pc);
        Serial.println("Measurement Started");

        if (mode.equals("scan"))
        {
            scan_done = false;
        }
        else if (mode.equals("mppt"))
        {
            mppt_done = false;
        }
        else if (mode.equals("constantVoltage"))
        {
            constant_voltage_done = false;
        }
    }

    if (!scan_done)
    {
        voltage_range_scan = val1;
        voltage_step_size_scan = val2;
        area_of_collector_mppt = val3;
        measurements_per_step_scan = val4;
        measurement_rate_scan = val5;
        light_status = val6;
        light_control(light_status);

        scan(SCAN_FORWARD);
        scan(SCAN_BACKWARD);
        scan_done = true;
        light_control(0);
        Serial.println("Done!");
    }
    else if (!mppt_done)
    {
        voltage_starting_mppt = val1;
        voltage_step_size_mppt = val2;
        area_of_collector_mppt = val3;
        measurements_per_step_mppt = val4;
        measurement_delay_mppt = val5;
        measurement_time_mins_mppt = val6;
        light_control(1);

        perturbAndObserveClassic();
        mppt_done = true;
        light_control(0);
        Serial.println("Done!");
    }
    else if (!constant_voltage_done)
    {
        constant_voltage = val1;
        measurements_per_step_scan = val3;
        setConstantVoltage();
        constant_voltage_done = true;
        Serial.println("Done!");
    }
}