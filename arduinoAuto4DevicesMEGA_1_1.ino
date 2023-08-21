// version 1.0
// runs on arduion mega-2560-r3
// processor: ATMEGA2560

#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>
// extern TwoWire Wire;

// #define PIN_WIRE_SDA         (20u)
// #define PIN_WIRE_SCL         (21u)
// #define WIRE Wire
// #define PIN_Wire_SDA        (70u)
// #define PIN_Wire_SCL        (71u)

/* Assign a unique ID to each sensor at the same time */
Adafruit_INA219 ina219_0;
Adafruit_INA219 ina219_1;
Adafruit_INA219 ina219_2;
Adafruit_INA219 ina219_3;
Adafruit_INA219 ina219_4;
Adafruit_INA219 ina219_5;
Adafruit_INA219 ina219_6;
Adafruit_INA219 ina219_7;
Adafruit_INA219 ina219_8;
Adafruit_INA219 ina219_9;
Adafruit_INA219 ina219_10;
Adafruit_INA219 ina219_11;
Adafruit_INA219 ina219_12;
Adafruit_INA219 ina219_13;
Adafruit_INA219 ina219_14;
Adafruit_INA219 ina219_15;
Adafruit_INA219 ina219_16;
Adafruit_INA219 ina219_17;
Adafruit_INA219 ina219_18;
Adafruit_INA219 ina219_19;
Adafruit_INA219 ina219_20;
Adafruit_INA219 ina219_21;
Adafruit_INA219 ina219_22;
Adafruit_INA219 ina219_23;
Adafruit_INA219 ina219_24;
Adafruit_INA219 ina219_25;
Adafruit_INA219 ina219_26;
Adafruit_INA219 ina219_27;
Adafruit_INA219 ina219_28;
Adafruit_INA219 ina219_29;
Adafruit_INA219 ina219_30;
Adafruit_INA219 ina219_31;

// Adafruit_INA219 all_ina[] = {ina219_0, ina219_1, ina219_2, ina219_3, ina219_4, ina219_5, ina219_6, ina219_7};

// Adafruit_INA219 all_ina[] =  {ina219_0, ina219_1, ina219_2, ina219_3, ina219_4, ina219_5, ina219_6, ina219_7, ina219_8, ina219_9, ina219_10, ina219_11, ina219_12, ina219_13, ina219_14, ina219_15, ina219_16, ina219_17, ina219_18, ina219_19, ina219_20, ina219_21, ina219_22, ina219_23, ina219_24, ina219_25, ina219_26, ina219_27, ina219_28, ina219_29, ina219_30, ina219_31};
Adafruit_INA219 *all_ina[] =  {&ina219_0, &ina219_1, &ina219_2, &ina219_3, &ina219_4, &ina219_5, &ina219_6, &ina219_7,
                            &ina219_8, &ina219_9, &ina219_10, &ina219_11, &ina219_12, &ina219_13, &ina219_14, &ina219_15,
                            &ina219_16, &ina219_17, &ina219_18, &ina219_19, &ina219_20, &ina219_21, &ina219_22, &ina219_23,
                            &ina219_24, &ina219_25, &ina219_26, &ina219_27, &ina219_28, &ina219_29, &ina219_30, &ina219_31};

/* Assign a unique ID to each sensor at the same time */
Adafruit_MCP4725 dac_0;
Adafruit_MCP4725 dac_1;
Adafruit_MCP4725 dac_2;
Adafruit_MCP4725 dac_3;
Adafruit_MCP4725 dac_4;
Adafruit_MCP4725 dac_5;
Adafruit_MCP4725 dac_6;
Adafruit_MCP4725 dac_7;
Adafruit_MCP4725 dac_8;
Adafruit_MCP4725 dac_9;
Adafruit_MCP4725 dac_10;
Adafruit_MCP4725 dac_11;
Adafruit_MCP4725 dac_12;
Adafruit_MCP4725 dac_13;
Adafruit_MCP4725 dac_14;
Adafruit_MCP4725 dac_15;
Adafruit_MCP4725 dac_16;
Adafruit_MCP4725 dac_17;
Adafruit_MCP4725 dac_18;
Adafruit_MCP4725 dac_19;
Adafruit_MCP4725 dac_20;
Adafruit_MCP4725 dac_21;
Adafruit_MCP4725 dac_22;
Adafruit_MCP4725 dac_23;
Adafruit_MCP4725 dac_24;
Adafruit_MCP4725 dac_25;
Adafruit_MCP4725 dac_26;
Adafruit_MCP4725 dac_27;
Adafruit_MCP4725 dac_28;
Adafruit_MCP4725 dac_29;
Adafruit_MCP4725 dac_30;
Adafruit_MCP4725 dac_31;
// Adafruit_MCP4725 all_dac[] = {dac_0, dac_1, dac_2, dac_3, dac_4, dac_5, dac_6, dac_7};

// Adafruit_MCP4725 all_dac [] = {dac_0, dac_1, dac_2, dac_3, dac_4, dac_5, dac_6, dac_7}; //, dac_8, dac_9, dac_10, dac_11, dac_12, dac_13, dac_14, dac_15, dac_16, dac_17, dac_18, dac_19, dac_20, dac_21, dac_22, dac_23,dac_24, dac_25, dac_26, dac_27, dac_28, dac_29, dac_30, dac_31};

Adafruit_MCP4725 *all_dac [] = {&dac_0, &dac_1, &dac_2, &dac_3, &dac_4, &dac_5, &dac_6, &dac_7,
                            &dac_8, &dac_9, &dac_10, &dac_11, &dac_12, &dac_13, &dac_14, &dac_15,
                            &dac_16, &dac_17, &dac_18, &dac_19, &dac_20, &dac_21, &dac_22, &dac_23,
                            &dac_24, &dac_25, &dac_26, &dac_27, &dac_28, &dac_29, &dac_30, &dac_31,};


// initialize hexcode i2c addresses for mutliplexers
int TCAADR_INA[] = {0x70, 0x72, 0x74, 0x76};    // 112, 114, 116, 118
int TCAADR_DAC[] = {0x71, 0x73, 0x75, 0x77};    // 113, 115, 117, 119
int MULTALL[] = {0x70, 0x72, 0x74, 0x76,0x71, 0x73, 0x75, 0x77};
// int TCAADR_INA[] = {0x72, 0x72, 0x72, 0x72};    // 112, 114, 116, 118
// int TCAADR_DAC[] = {0x73, 0x73, 0x73, 0x73};    // 113, 115, 117, 119

int ARUDINOID = 0;

// INA219 Variables ---------------------------------------------------------------------
float shunt_voltage;
float bus_voltage;
float current_mA;
float load_voltage;
float power_mW;
float current_mA_Flipped;

// Serial Input Variables ---------------------------------------------------------------
float val1;
float val2;
int val3;
int val4;
int val5;
const byte num_chars = 1000;
char receivedChars[num_chars];
char tempChars[num_chars];        // temporary array for use when parsing

// used to aid in parsing through input data
char mode_from_pc[num_chars] = {0};
boolean new_data = false;

// Perturb and Observe  Variables -------------------------------------------------------
boolean pno_done = true;
float pno_starting_voltage      = 0.0;
float pno_voltage_step_size    = 0.000;
int pno_measurement_delay       = 0;
int pno_measurements_per_step   = 0;
unsigned long pno_measurement_time  = 0;
const int MAXVOLTAGEPNO = 2;
int dummy;
float Vset[4][8];

// Scan Variables -----------------------------------------------------------------------
boolean scan_done = true;
float avg_volt[4][8];
float avg_curr[4][8];
int volt_step_count = 0;
float VOLTAGE_SET_VAL   = 0;
uint16_t dac_val    = 0;
float scan_voltage_range       = 0.0;
float scan_voltage_step_size   = 0.000;
int scan_measurements_per_step = 0;
int scan_measurement_rate      = 0;
int light_status = 0;


void setup(void) {
    //pins
    pinMode(10, OUTPUT);
    pinMode(11, OUTPUT);
    pinMode(12, OUTPUT);
    digitalWrite(10, HIGH);
    digitalWrite(11, HIGH);
    digitalWrite(12, HIGH);



    //system setup
    Wire.begin();

    // set baud rate
    Serial.begin(115200);
    while (!Serial)
    {
        delay(10);
    }

    // initialize sensors
    // I2C device found at address 0x40  !
    // I2C device found at address 0x62  !
    // I2C device found at address 0x70  !
    // I2C device found at address 0x71  !
    // I2C device found at address 0x72  !
    // I2C device found at address 0x73  !
    // I2C device found at address 0x74  !
    // I2C device found at address 0x75  !
    // I2C device found at address 0x76  !
    // I2C device found at address 0x77  !
    for (uint8_t DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (uint8_t PIXEL = 0; PIXEL < 8; PIXEL++) {
            // Serial.print(PIXEL);
            // Serial.print(",");
            // Serial.println(TCAADR_INA[DEVICE]);
            setup_ina219(all_ina[PIXEL+8*DEVICE], PIXEL, TCAADR_INA[DEVICE]);
            // setup_ina219(all_ina[PIXEL+8*DEVICE], PIXEL, 0x70);
        }
    }

    for (uint8_t DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (uint8_t PIXEL = 0; PIXEL < 8; PIXEL++) {
            // Serial.print(PIXEL);
            // Serial.print(",");
            // Serial.println(TCAADR_DAC[DEVICE]);
            setup_dac(all_dac[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE]);
            // setup_dac(all_dac[PIXEL+8*DEVICE], PIXEL, 0x70);
        }
    }



    Serial.println("");
    Serial.println("setup completed");
}


void loop(void) {
    recv_with_start_end_markers(); // get data from computer
    if (new_data == true && scan_done && pno_done) {
        strcpy(tempChars, receivedChars);
        parse_data();
        show_parsed_data();
        // zero();

        new_data = false;
        String mode = String(mode_from_pc);

        if (mode.equals("scan")) {
            scan_done = false;
        } else if (mode.equals("PnO")) {

            pno_done = false;

        }
    }

    if (!scan_done) {
        // Serial.println("Scanning");
        // scan_voltage_range = 1.2;
        // scan_voltage_step_size = 0.01;
        // scan_measurements_per_step= 5;
        // scan_measurement_rate = 50;
        // scan("backward");
        scan_voltage_range = val1;
        scan_voltage_step_size = val2;
        scan_measurements_per_step = val3;
        scan_measurement_rate = val4;
        light_status = val5;
        light_control(light_status);
        scan("backward");
        scan("forward");
        scan_done = true;
        Serial.println("Done!");

        // const byte num_chars = 32;
        // char receivedChars[num_chars];
        // char tempChars[num_chars];        // temporary array for use when parsing

        // // used to aid in parsing through input data
        // char mode_from_pc[num_chars] = {0};
        // boolean new_data = false;

    } else if (!pno_done) {
        Serial.println("Perturb and Observe");

        pno_starting_voltage = val1;
        pno_voltage_step_size = val2;
        pno_measurements_per_step= val3;
        pno_measurement_delay = val4;
        pno_measurement_time = val5;

        pertube_and_observe();
        Serial.println("Done!");
        // const byte num_chars = 32;
        // char receivedChars[num_chars];
        // char tempChars[num_chars];        // temporary array for use when parsing

        // // used to aid in parsing through input data
        // char mode_from_pc[num_chars] = {0};
        // boolean new_data = false;
    }


}


// Main Methods =========================================================================
/*
Algo to search for maximum PCE along voltage range.
Find PCE at current voltage,
find PCE above and below by a set voltage amount,
then set new voltage to highest PCE



enter loop (stops when total time is met) {
    32x set voltage to Vset
    delay time
    loop (5x): 32x read voltage

    32x set voltage to Vset + step size
    delay time
    loop (5x): 32x read voltage

    32x set voltage to Vset - step size
    delay time
    loop (5x): 32x read voltage

    perform calculations
    (depending on which one has the highest power)
    Vset = Vset/Vset+/Vset-

    return to start of loop
*/
void pertube_and_observe() {
    led(true);
    light_control(1);

    // float Vset[4][8];
    float VsetUp;
    float VsetDown;
    float time;

    int count;

    // Set starting voltage level on each dac
    // for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
    //     for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
    //         Vset[DEVICE][PIXEL] = pno_starting_voltage;
    //     }
    // }

    float avgPowerCalced[4][8];
    float avgPowerCalcedUp[4][8];
    float avgPowerCalcedDown[4][8];
    float load_voltageArr[4][8];
    float current_mA_FlippedArr[4][8];
    float PCE[4][8];
    pno_measurements_per_step++; //average not working correctly

    int currentMillis = 0;
    int pm = millis();
    int startMillis = millis();

    // // input time in hours
    // Serial.print("pno_measurement_time (hours): ");
    // Serial.println(pno_measurement_time);
    // Serial.print("pno_measurement_time (days): ");
    // Serial.println(pno_measurement_time/24.0);
    // pno_measurement_time *= 60*60;

    // // input time in minutes
    Serial.print("pno_measurement_time (mins): ");
    Serial.println(pno_measurement_time);
    Serial.print("pno_measurement_time (hours): ");
    Serial.println(pno_measurement_time/60.0);
    pno_measurement_time *= 60.0;


    // for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
    //     for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
    //         Serial.println(Vset[DEVICE][PIXEL]);
    //     }
    // }



    while((millis()-startMillis)/1000.0 < pno_measurement_time) { // convert millis to seconds
        // Vset -------------------------------------------------------------------------------------------------------
        // 32x set voltage to Vset
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                // Serial.println(Vset[DEVICE][PIXEL]);
                if (MAXVOLTAGEPNO < Vset[DEVICE][PIXEL]) {
                    Vset[DEVICE][PIXEL] = MAXVOLTAGEPNO;
                }
                set_voltage(all_dac[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], Vset[DEVICE][PIXEL]);
                // delay(pno_measurement_delay);
            }
            delay(pno_measurement_delay);
        }
        // delay time
        // delay(pno_measurement_delay);
        // loop (pno_measurements_per_step): 32x read voltage
        for (int i = 0; i < pno_measurements_per_step; ++i) {
            // getINA129(&all_ina219[ID], ID);
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    get_volt_and_curr(all_ina[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                    avgPowerCalced[DEVICE][PIXEL] += load_voltage * current_mA_Flipped;
                    load_voltageArr[DEVICE][PIXEL] += load_voltage;
                    current_mA_FlippedArr[DEVICE][PIXEL] += current_mA_Flipped;
                }
            }
        }

        // Vset + Step Size -------------------------------------------------------------------------------------------
        // 32x set voltage to Vset + step size
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                VsetUp = Vset[DEVICE][PIXEL] + pno_voltage_step_size;
                set_voltage(all_dac[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], VsetUp);
                // delay(pno_measurement_delay);
            }
            delay(pno_measurement_delay);
        }
        // delay time
        // delay(pno_measurement_delay);
        // loop (5x): 32x read voltage
        for (int i = 0; i < pno_measurements_per_step; ++i) {
            // getINA129(&all_ina219[ID], ID);
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    get_volt_and_curr(all_ina[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                    avgPowerCalcedUp[DEVICE][PIXEL] += load_voltage * current_mA_Flipped;
                }
            }
        }


        // Vset - Step Size -------------------------------------------------------------------------------------------
        // 32x set voltage to Vset + step size
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                VsetDown = Vset[DEVICE][PIXEL] - pno_voltage_step_size;
                set_voltage(all_dac[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], VsetDown);
                // delay(pno_measurement_delay);
            }
            delay(pno_measurement_delay);
        }
        // delay time
        // delay(pno_measurement_delay);
        // loop (5x): 32x read voltage
        for (int i = 0; i < pno_measurements_per_step; ++i) {
            // getINA129(&all_ina219[ID], ID);
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    get_volt_and_curr(all_ina[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                    avgPowerCalcedDown[DEVICE][PIXEL] += load_voltage * current_mA_Flipped;
                }
            }
        }
        // Calculations -----------------------------------------------------------------------------------------------
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                avgPowerCalced[DEVICE][PIXEL] = avgPowerCalced[DEVICE][PIXEL]/pno_measurements_per_step;
                avgPowerCalcedUp[DEVICE][PIXEL] = avgPowerCalcedUp[DEVICE][PIXEL]/pno_measurements_per_step;
                avgPowerCalcedDown[DEVICE][PIXEL] = avgPowerCalcedDown[DEVICE][PIXEL]/pno_measurements_per_step;
                load_voltageArr[DEVICE][PIXEL] = load_voltageArr[DEVICE][PIXEL]/pno_measurements_per_step;
                current_mA_FlippedArr[DEVICE][PIXEL] = current_mA_FlippedArr[DEVICE][PIXEL]/pno_measurements_per_step;

                if (avgPowerCalcedUp[DEVICE][PIXEL] > avgPowerCalcedDown[DEVICE][PIXEL] && avgPowerCalcedUp[DEVICE][PIXEL] > avgPowerCalced[DEVICE][PIXEL]) {
                    Vset[DEVICE][PIXEL] += pno_voltage_step_size;
                } else if (avgPowerCalcedDown[DEVICE][PIXEL] > avgPowerCalcedUp[DEVICE][PIXEL] && avgPowerCalcedDown[DEVICE][PIXEL] > avgPowerCalced[DEVICE][PIXEL]) {
                    Vset[DEVICE][PIXEL] -= pno_voltage_step_size;
                }

                PCE[DEVICE][PIXEL] = (avgPowerCalced[DEVICE][PIXEL]/1000)/(0.1*0.128); // PCE calcuation assuming pixel area of 0.128 cm^2

            }
        }



        // print out values to send them to PC
        currentMillis = currentMillis + millis() - pm;
        pm = millis();
        Serial.print((millis()-startMillis)/1000.0, 4);
        Serial.print(", ");

        // UNCOMMENT TO SHOW VOLTAGE AND CURRENT FOR EVERY PIXEL
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                Serial.print(load_voltageArr[DEVICE][PIXEL], 2);
                Serial.print(", ");
                Serial.print(current_mA_FlippedArr[DEVICE][PIXEL], 2);
                Serial.print(", ");
            }
        }

        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
            Serial.print((PCE[DEVICE][PIXEL]*100), 4);
            Serial.print(", ");
            }
        }
        Serial.print(ARUDINOID);

        Serial.println("");
    }


    pno_done = true;
    led(false);

}

// performs forward and/or backward JV scan of solar cell
void scan(String dir) {
    led(true);

    int s = (scan_voltage_range*1000)/scan_measurement_rate;
    int steps = (scan_voltage_range*1000)/(scan_voltage_step_size*1000);
    // Serial.print(s); Serial.print(" "); Serial.println (steps);


    // amount of time it takes to take measurement from all 8 ina219 on ARDUINO UNO
    // must change this on different setup
    // uint8_t OFFSET = 35*8;

    int delayTimeMS = 20; //(s*1000)/steps - (OFFSET * scan_measurements_per_step);
    if (delayTimeMS < 0) {
        delayTimeMS = 0;
    }


    Serial.print("started scan with delay time: "); Serial.println(delayTimeMS);

    float upperVoltageLimit;
    if (dir == "backward") {
        VOLTAGE_SET_VAL = scan_voltage_range + scan_voltage_step_size;
        upperVoltageLimit = scan_voltage_range + scan_voltage_step_size;
    } else if (dir == "forward") {
        VOLTAGE_SET_VAL = 0;
        upperVoltageLimit = scan_voltage_range - scan_voltage_step_size;
    }

    for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
            set_voltage(all_dac[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], VOLTAGE_SET_VAL);
        }
    }

    delay(delayTimeMS);
    unsigned long startMillis = millis();

    while (upperVoltageLimit >= VOLTAGE_SET_VAL && VOLTAGE_SET_VAL >= 0) {
        // Serial.print(millis()); Serial.print(" "); Serial.println(volt_step_count); // used to measure offset
        if (volt_step_count > scan_measurements_per_step) {
            if (dir == "backward") {
                VOLTAGE_SET_VAL -= scan_voltage_step_size;
            } else if (dir == "forward") {
                VOLTAGE_SET_VAL += scan_voltage_step_size;
            }

            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    set_voltage(all_dac[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], VOLTAGE_SET_VAL);
                }
            }


            delay(delayTimeMS);                    //to set the scan rate

            unsigned long currMillis = millis() - startMillis;
            Serial.print(currMillis/1000.0, 4);
            Serial.print(",");
            Serial.print(VOLTAGE_SET_VAL);
            Serial.print(",");
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    Serial.print(avg_volt[DEVICE][PIXEL]/volt_step_count, 4);
                    Serial.print(",");
                    Serial.print(avg_curr[DEVICE][PIXEL]/volt_step_count, 4);
                    Serial.print(",");
                }
            }
            Serial.print(ARUDINOID);
            Serial.println("");

            // reset all values in array to 0
            memset(avg_volt, 0.0, sizeof(avg_volt));
            memset(avg_curr, 0.0, sizeof(avg_curr));
            volt_step_count = 0;
        } else {
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    get_volt_and_curr(all_ina[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                    avg_volt[DEVICE][PIXEL] += load_voltage;
                    avg_curr[DEVICE][PIXEL] += current_mA_Flipped;
                }
            }
            volt_step_count++;



        }
    }

    scan_done = true;
    led(false);
}


// Helper Methods =======================================================================
void setup_ina219(Adafruit_INA219 *ina219, uint8_t PIXEL, uint8_t tcaADDR) {
    // Serial.print("ina219 setup started");
    // PIXEL = PIXEL%8;
    // Serial.print(PIXEL);
    TCA9548Access(PIXEL, tcaADDR);
    if (!ina219->begin())
    {
        Serial.print(tcaADDR);
        Serial.print("ina219_");
        Serial.print(PIXEL);
        Serial.println(" not detected");
        // creates endless loop to stop program
        // while (1);
    }
    ina219->setCalibration_16V_400mA();
    // Serial.print("INA219_"); Serial.print(ID); Serial.println(" is setup");
}

void setup_dac(Adafruit_MCP4725 *dac, uint8_t PIXEL, uint8_t tcaADDR) {
    // Serial.print("mcp4725 setup started");
    // PIXEL = PIXEL%8;
    TCA9548Access(PIXEL, tcaADDR);
    if (!dac->begin())
    {
        Serial.print(tcaADDR);
        Serial.print("dac_");
        Serial.print(PIXEL);
        Serial.println(" not detected");
        // creates endless loop to stop program
        // while (1);
    }
    // Serial.print("INA219_"); Serial.print(ID); Serial.println(" is setup");

}

void TCA9548Access(uint8_t PIXEL, int bus) {
    // Wire.beginTransmission(bus); // address for specific Multiplexer
    // Wire.write(1 << PIXEL);         // select pixel
    // Wire.endTransmission();
    for (int DEVICE = 0; DEVICE < 8; DEVICE++) {
        if (MULTALL[DEVICE]!=bus){
            Wire.beginTransmission(MULTALL[DEVICE]); // address for specific Multiplexer
            Wire.write(0);         // set as zero
            Wire.endTransmission();
        }
    }
    Wire.beginTransmission(bus); // address for specific Multiplexer
            Wire.write(1 << PIXEL);         // select pixel
            Wire.endTransmission();

}

// void TCA9548A_INA219(uint8_t bus) {
//     // Serial.print("TCA channel "); Serial.print(bus); Serial.println(" activated");
//     Wire.beginTransmission(0x72); // TCA9548A_INA219 address is 0x70
//     Wire.write(1 << bus);         // send byte to select bus
//     Wire.endTransmission();

// }

// void TCA9548A_MCP475(uint8_t bus) {
//     Wire.beginTransmission(0x73); // TCA9548A_MCP475 address is 0x71
//     Wire.write(1 << bus);         // send byte to select bus
//     Wire.endTransmission();
//     // Serial.print("TCA channel "); Serial.print(bus); Serial.println(" activated");
// }

void led(boolean status) {
    if (status) {
        digitalWrite(LED_BUILTIN, HIGH);
    } else {
        digitalWrite(LED_BUILTIN, LOW);
    }
}

void show_parsed_data() {
    Serial.print("Val1: ");
    Serial.print(val1);
    Serial.print(", Val2: ");
    Serial.print(val2);
    Serial.print(", Val3: ");
    Serial.print(val3);
    Serial.print(", Val4: ");
    Serial.print(val4);
    Serial.print(", Val5: ");
    Serial.print(val5);
    Serial.println("");
}


void recv_with_start_end_markers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && new_data == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= num_chars) {
                    ndx = num_chars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                new_data = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

// split the data into its parts
// void parse_data() {

//     char * strtokIndx; // this is used by strtok() as an index

//     strtokIndx = strtok(tempChars,",");      // get the first part - the string
//     strcpy(mode_from_pc, strtokIndx); // copy it to mode_from_pc
//     Serial.println(mode_from_pc);

//     strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
//     val1 = atof(strtokIndx);     // convert this part to an float

//     strtokIndx = strtok(NULL, ",");
//     val2 = atof(strtokIndx);     // convert this part to a float

//     strtokIndx = strtok(NULL, ",");
//     val3 = atoi(strtokIndx);     // convert this part to a int

//     strtokIndx = strtok(NULL, ",");
//     val4 = atoi(strtokIndx);     // convert this part to a int

//     strtokIndx = strtok(NULL, ",");
//     val5 = atoi(strtokIndx);     // convert this part to a int

// }

// takes input of vmpp points from jv curve for pno
void parse_data() {
    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(mode_from_pc, strtokIndx); // copy it to the mode

    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    val1 = atof(strtokIndx);     // convert this part to an float

    strtokIndx = strtok(NULL, ",");
    val2 = atof(strtokIndx);     // convert this part to a float

    strtokIndx = strtok(NULL, ",");
    val3 = atoi(strtokIndx);     // convert this part to a int

    strtokIndx = strtok(NULL, ",");
    val4 = atoi(strtokIndx);     // convert this part to a int

    strtokIndx = strtok(NULL, ",");
    val5 = atoi(strtokIndx);     // convert this part to a int

    for (uint8_t DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (uint8_t PIXEL = 0; PIXEL < 8; PIXEL++) {
            strtokIndx = strtok(NULL, ",");
            // Serial.print("MESSSAGE,");
            // Serial.println(atof(strtokIndx));
            Vset[DEVICE][PIXEL] = atof(strtokIndx);     // convert this part to a float
        }
    }

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

// zeros all the values on the dac
void zero() {
    for (uint8_t DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (uint8_t PIXEL = 0; PIXEL < 8; PIXEL++) {
            set_voltage(all_dac[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], 0);
        }
    }

}

// set the DAC voltage output
void set_voltage(Adafruit_MCP4725 *dac,
                uint8_t PIXEL,
                uint8_t tcaADDR,
                float VOLTAGE_SET_VAL) {
    // for (int i = 0; i < 4; i++) {
    //     for (int j = 0; j < 8; j++) {
    TCA9548Access(PIXEL, tcaADDR);
    dac -> set_voltage(convert_to_12bit(VOLTAGE_SET_VAL), false);
        // }
    // }
}

// get new values from ina219
void get_volt_and_curr(Adafruit_INA219 *ina219, uint8_t tcaADDR, uint8_t PIXEL) {
    TCA9548Access(PIXEL, tcaADDR);
    shunt_voltage       = ina219 -> getshunt_voltage_mV();
    bus_voltage         = ina219 -> getbus_voltage_V();
    current_mA         = ina219 -> getCurrent_mA();
    power_mW           = ina219 -> getPower_mW();
    current_mA_Flipped = current_mA * -1;
    load_voltage        = bus_voltage + (shunt_voltage / 1000);
}

// TODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODO
void light_control(int light_status) {
    if (light_status == 0) {
        Serial.println("turned light off");
    } else if (light_status == 1) {
        Serial.println("turned light on");
    }

}



