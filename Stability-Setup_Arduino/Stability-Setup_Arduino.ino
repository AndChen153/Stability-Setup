// main.ino
#include <EEPROM.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

#include "include/sensor.h"
#include "include/serial_com.h"
#include "include/helper.h"
#include "include/measurement.h"

const int idAddress = 0;
uint32_t uniqueID;

bool init_success = true;

byte relayPin = 7;

char received_chars[NUM_CHARS];
char str_param[MAX_MODE_LEN];
char mode[MAX_MODE_LEN];

// Perturb and Observe Variables
volatile bool mppt_done = true;

float vset[8] = {0.0,0.0,0.0,0.0,0.0,0.0};
float mppt_step_size_V = 0.000;
int mppt_measurements_per_step = 0;
int mppt_delay = 0;
int mppt_measurement_interval = 0;
unsigned long mppt_time_mins = 0;

// Scan Variables
volatile bool scan_done = true;
float avg_volt[8];
float avg_curr[8];
int volt_step_count = 0;
float voltage_val = 0;

float scan_range = 0.0;
float scan_step_size = 0.000;
int scan_read_count = 0;
int scan_rate = 0;
int light_status = 0;

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
    if (init_success){
        Serial.println("Arduino Ready");
    }
    else {
        Serial.println("Sensor Initialization Failed. Please Check Connection.");
    }
}

void loop(void)
{
    measurement_running = !scan_done || !constant_voltage_done || !mppt_done;
    if (recvWithLineTermination() == serialCommResult::START)
    {
        zero();

        Serial.println("Measurement Started");

        if (strcmp(mode, "scan") == 0)
        {
            scan_done = false;
        }
        else if (strcmp(mode, "mppt") == 0)
        {
            mppt_done = false;
        }
        else if (strcmp(mode, "scan") == 0)
        {
            constant_voltage_done = false;
        }
        measurement_running = !scan_done || !constant_voltage_done || !mppt_done;
    }

    if (!scan_done)
    {
        light_control(light_status);
        scan(SCAN_FORWARD);
        scan(SCAN_BACKWARD);
        scan_done = true;
        light_control(0);
        Serial.println("Done!");
    }
    else if (!mppt_done)
    {
        light_control(1);
        perturbAndObserveClassic();
        mppt_done = true;
        light_control(0);
        Serial.println("Done!");
    }
    else if (!constant_voltage_done)
    {
        setConstantVoltage();
    constant_voltage_done = true;
        Serial.println("Done!");
    }
}