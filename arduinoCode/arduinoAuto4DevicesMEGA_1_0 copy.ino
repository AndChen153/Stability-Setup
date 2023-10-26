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

// Adafruit_INA219 allINA[] = {ina219_0, ina219_1, ina219_2, ina219_3, ina219_4, ina219_5, ina219_6, ina219_7};

// Adafruit_INA219 allINA[] =  {ina219_0, ina219_1, ina219_2, ina219_3, ina219_4, ina219_5, ina219_6, ina219_7, ina219_8, ina219_9, ina219_10, ina219_11, ina219_12, ina219_13, ina219_14, ina219_15, ina219_16, ina219_17, ina219_18, ina219_19, ina219_20, ina219_21, ina219_22, ina219_23, ina219_24, ina219_25, ina219_26, ina219_27, ina219_28, ina219_29, ina219_30, ina219_31};
Adafruit_INA219 *allINA[] =  {&ina219_0, &ina219_1, &ina219_2, &ina219_3, &ina219_4, &ina219_5, &ina219_6, &ina219_7,
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
// Adafruit_MCP4725 allDAC[] = {dac_0, dac_1, dac_2, dac_3, dac_4, dac_5, dac_6, dac_7};

// Adafruit_MCP4725 allDAC [] = {dac_0, dac_1, dac_2, dac_3, dac_4, dac_5, dac_6, dac_7}; //, dac_8, dac_9, dac_10, dac_11, dac_12, dac_13, dac_14, dac_15, dac_16, dac_17, dac_18, dac_19, dac_20, dac_21, dac_22, dac_23,dac_24, dac_25, dac_26, dac_27, dac_28, dac_29, dac_30, dac_31};

Adafruit_MCP4725 *allDAC [] = {&dac_0, &dac_1, &dac_2, &dac_3, &dac_4, &dac_5, &dac_6, &dac_7,
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
float shuntvoltage;
float busvoltage;
float current_mA;
float loadvoltage;
float power_mW;
float current_mA_Flipped;

// Serial Input Variables ---------------------------------------------------------------
float val1;
float val2;
int val3;
int val4;
int val5;
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

// used to aid in parsing through input data
char messageFromPC[numChars] = {0};
boolean newData = false;

// Perturb and Observe  Variables -------------------------------------------------------
boolean perturb_And_ObserveDone = true;
float voltage_Starting_PnO      = 0.0;
float voltage_Step__Size_PnO    = 0.000;
int measurement_Delay_PnO       = 0;
int measurements_Per_Step_PnO   = 0;
unsigned long measurement_Time  = 0;
int dummy;

// Tracking and Scanning Variables ------------------------------------------------------
boolean tracking_And_ScanningDone = true;

float voltage_Starting_TaS    = 0.0;
float voltage_Step__Size_TaS  = 0.000;
int measurement_Delay_TaS     = 0;
int measurements_Per_Step_TaS = 0;

// Scan Variables -----------------------------------------------------------------------
boolean scanDone = true;
float avgVolt[4][8];
float avgCurr[4][8];
int volt_Step_Count = 0;
float VOLTAGE_SET_VAL   = 0;
uint16_t dac_val    = 0;
float voltage_Range_Scan       = 0.0;
float voltage_Step_Size_Scan   = 0.000;
int measurements_Per_Step_Scan = 0;
int measurement_Rate_Scan      = 0;
int light_Status = 0;


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
            setupSensor_INA219(allINA[PIXEL+8*DEVICE], PIXEL, TCAADR_INA[DEVICE]);
            // setupSensor_INA219(allINA[PIXEL+8*DEVICE], PIXEL, 0x70);
        }
    }

    for (uint8_t DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (uint8_t PIXEL = 0; PIXEL < 8; PIXEL++) {
            // Serial.print(PIXEL);
            // Serial.print(",");
            // Serial.println(TCAADR_DAC[DEVICE]);
            setupSensor_Dac(allDAC[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE]);
            // setupSensor_Dac(allDAC[PIXEL+8*DEVICE], PIXEL, 0x70);
        }
    }



    Serial.println("");
    Serial.println("setup completed");
}


void loop(void) {
    recvWithStartEndMarkers(); // get data from computer
    if (newData == true && scanDone && tracking_And_ScanningDone) {
        strcpy(tempChars, receivedChars);
        parseData();
        showParsedData();
        // zero();

        newData = false;
        String mode = String(messageFromPC);

        if (mode.equals("scan")) {
            scanDone = false;
        } else if (mode.equals("PnO")) {
            perturb_And_ObserveDone = false;
        }
    }

    if (!scanDone) {
        // Serial.println("Scanning");
        // voltage_Range_Scan = 1.2;
        // voltage_Step_Size_Scan = 0.01;
        // measurements_Per_Step_Scan= 5;
        // measurement_Rate_Scan = 50;
        // scan("backward");
        voltage_Range_Scan = val1;
        voltage_Step_Size_Scan = val2;
        measurements_Per_Step_Scan = val3;
        measurement_Rate_Scan = val4;
        light_Status = val5;
        lightControl(light_Status);
        scan("backward");
        scan("forward");
        scanDone = true;
        Serial.println("Done!");

    } else if (!perturb_And_ObserveDone) {
        Serial.println("Perturb and Observe");

        voltage_Starting_PnO = val1;
        voltage_Step__Size_PnO = val2;
        measurements_Per_Step_PnO= val3;
        measurement_Delay_PnO = val4;
        measurement_Time = val5;

        perturbAndObserve();
        Serial.println("Done!");
    }


}


// Main Methods =========================================================================

void perturbAndObserve() {
    led(true);
    lightControl(1);

    float Vset[4][8];
    float VsetUp;
    float VsetDown;
    float time;

    int count;

    // Set starting voltage level on each dac
    for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
            Vset[DEVICE][PIXEL] = voltage_Starting_PnO;
        }
    }
    // for (int ID = 0; ID < 8; ID ++) {
    //     Vset[ID] = voltage_Starting_PnO;
    // }


    float avgPowerCalced[4][8];
    float avgPowerCalcedUp;
    float avgPowerCalcedDown;
    float loadvoltageArr[4][8];
    float current_mA_FlippedArr[4][8];
    float PCE[4][8];
    measurements_Per_Step_PnO++; //average not working correctly

    int currentMillis = 0;
    int pm = millis();
    int startMillis = millis();
    Serial.print("measurement_Time (hours): ");
    Serial.println(measurement_Time);
    measurement_Time *= 60*60;

    Serial.print("measurement_Time (days): ");
    Serial.println(measurement_Time/60.0/24.0);
    for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
            // currentMillis = currentMillis + millis() - pm;
            // pm = millis();
            // Serial.println((millis()-startMillis)/1000.0, 4);
            // Vset --------------------------------------------------
            setVoltage(allDAC[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], Vset[DEVICE][PIXEL]);
            delay(measurement_Delay_PnO);
            for (int i = 0; i < measurements_Per_Step_PnO; ++i) {
                // getINA129(&allINA219[ID], ID);
                getVolCurr(allINA[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                avgPowerCalced[DEVICE][PIXEL] += loadvoltage * current_mA_Flipped;
                loadvoltageArr[DEVICE][PIXEL] += loadvoltage;
                current_mA_FlippedArr[DEVICE][PIXEL] += current_mA_Flipped;
            }
        }
    }
    while((millis()-startMillis)/1000.0 < measurement_Time) { // convert millis to same unit as measurement time input
        /*
        Algo to search for maximum PCE along voltage range.
        Find PCE at current voltage,
        find PCE above and below by a set voltage amount,
        then set new voltage to highest PCE
        */
        
        // Vset + deltaV -----------------------------------------
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {

                VsetUp = Vset[DEVICE][PIXEL] + voltage_Step__Size_PnO;
                setVoltage(allDAC[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], Vset[DEVICE][PIXEL]);
                delay(measurement_Delay_PnO);
            }
        }

        for (int i = 0; i < measurements_Per_Step_PnO; ++i) {
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    // getINA129(&allINA219[ID], ID);
                    getVolCurr(allINA[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                    avgPowerCalcedUp += loadvoltage * current_mA_Flipped;
                }
            }
        }
        

        // Vset - deltaV -----------------------------------------
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                VsetDown = Vset[DEVICE][PIXEL] - voltage_Step__Size_PnO;
                setVoltage(allDAC[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], Vset[DEVICE][PIXEL]);
                delay(measurement_Delay_PnO);

                
            }
        }
        
        for (int i = 0; i < measurements_Per_Step_PnO; ++i) {
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    getVolCurr(allINA[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                    avgPowerCalcedDown += loadvoltage * current_mA_Flipped;
                }
            }
        }

        // Calculations ------------------------------------------
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                
                avgPowerCalced[DEVICE][PIXEL] = avgPowerCalced[DEVICE][PIXEL]/measurements_Per_Step_PnO;
                avgPowerCalcedUp = avgPowerCalcedUp/measurements_Per_Step_PnO;
                avgPowerCalcedDown = avgPowerCalcedDown/measurements_Per_Step_PnO;
                loadvoltageArr[DEVICE][PIXEL] = loadvoltageArr[DEVICE][PIXEL]/measurements_Per_Step_PnO;
                current_mA_FlippedArr[DEVICE][PIXEL] = current_mA_FlippedArr[DEVICE][PIXEL]/measurements_Per_Step_PnO;

                if (avgPowerCalcedUp > avgPowerCalcedDown && avgPowerCalcedUp > avgPowerCalced[DEVICE][PIXEL]) {
                    Vset[DEVICE][PIXEL] += voltage_Step__Size_PnO;
                } else if (avgPowerCalcedDown > avgPowerCalcedUp && avgPowerCalcedDown > avgPowerCalced[DEVICE][PIXEL]) {
                    Vset[DEVICE][PIXEL] -= voltage_Step__Size_PnO;
                }

                PCE[DEVICE][PIXEL] = (avgPowerCalced[DEVICE][PIXEL]/1000)/(0.1*0.128); // PCE calcuation assuming pixel area of 0.128 cm^2
            }
        }

        
        // Vset --------------------------------------------------
        for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
            for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                // currentMillis = currentMillis + millis() - pm;
                // pm = millis();
                // Serial.println((millis()-startMillis)/1000.0, 4);
                
                setVoltage(allDAC[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], Vset[DEVICE][PIXEL]);
                delay(measurement_Delay_PnO);
                
            }
        }

        for (int i = 0; i < measurements_Per_Step_PnO; ++i) {
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    // getINA129(&allINA219[ID], ID);
                    getVolCurr(allINA[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                    avgPowerCalced[DEVICE][PIXEL] += loadvoltage * current_mA_Flipped;
                    loadvoltageArr[DEVICE][PIXEL] += loadvoltage;
                    current_mA_FlippedArr[DEVICE][PIXEL] += current_mA_Flipped;
                }
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
                Serial.print(loadvoltageArr[DEVICE][PIXEL], 2);
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


    perturb_And_ObserveDone = true;
    led(false);

}

// performs forward and/or backward JV scan of solar cell
void scan(String dir) {
    led(true);

    int s = (voltage_Range_Scan*1000)/measurement_Rate_Scan;
    int steps = (voltage_Range_Scan*1000)/(voltage_Step_Size_Scan*1000);
    // Serial.print(s); Serial.print(" "); Serial.println (steps);


    // amount of time it takes to take measurement from all 8 ina219 on ARDUINO UNO
    // must change this on different setup
    uint8_t OFFSET = 35;

    int delayTimeMS = (s*1000)/steps - (OFFSET * measurements_Per_Step_Scan);
    if (delayTimeMS < 0) {delayTimeMS = 0;}

    Serial.print("started scan with delay time: "); Serial.println(delayTimeMS);

    float upperVoltageLimit;
    if (dir == "backward") {
        VOLTAGE_SET_VAL = voltage_Range_Scan + voltage_Step_Size_Scan;
        upperVoltageLimit = voltage_Range_Scan + voltage_Step_Size_Scan;
    } else if (dir == "forward") {
        VOLTAGE_SET_VAL = 0;
        upperVoltageLimit = voltage_Range_Scan - voltage_Step_Size_Scan;
    }

    for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
        for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
            setVoltage(allDAC[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], VOLTAGE_SET_VAL);
        }
    }

    delay(delayTimeMS);
    unsigned long startMillis = millis();

    while (upperVoltageLimit >= VOLTAGE_SET_VAL && VOLTAGE_SET_VAL >= 0) {
        // Serial.print(millis()); Serial.print(" "); Serial.println(volt_Step_Count); // used to measure offset
        if (volt_Step_Count > measurements_Per_Step_Scan) {
            if (dir == "backward") {
                VOLTAGE_SET_VAL -= voltage_Step_Size_Scan;
            } else if (dir == "forward") {
                VOLTAGE_SET_VAL += voltage_Step_Size_Scan;
            }

            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    setVoltage(allDAC[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], VOLTAGE_SET_VAL);
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
                    Serial.print(avgVolt[DEVICE][PIXEL]/volt_Step_Count, 4);
                    Serial.print(",");
                    Serial.print(avgCurr[DEVICE][PIXEL]/volt_Step_Count, 4);
                    Serial.print(",");
                }
            }
            Serial.print(ARUDINOID);
            Serial.println("");

            // reset all values in array to 0
            memset(avgVolt, 0.0, sizeof(avgVolt));
            memset(avgCurr, 0.0, sizeof(avgCurr));
            volt_Step_Count = 0;
        } else {
            for (int DEVICE = 0; DEVICE < 4; DEVICE++) {
                for (int PIXEL = 0; PIXEL < 8; PIXEL++) {
                    getVolCurr(allINA[PIXEL+8*DEVICE], TCAADR_INA[DEVICE], PIXEL);
                    avgVolt[DEVICE][PIXEL] += loadvoltage;
                    avgCurr[DEVICE][PIXEL] += current_mA_Flipped;
                }
            }
            volt_Step_Count++;



        }
    }

    scanDone = true;
    led(false);
}


// Helper Methods =======================================================================

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void setupSensor_INA219(Adafruit_INA219 *ina219, uint8_t PIXEL, uint8_t tcaADDR) {
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

void setupSensor_Dac(Adafruit_MCP4725 *dac, uint8_t PIXEL, uint8_t tcaADDR) {
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

void showParsedData() {
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

// split the data into its parts
void parseData() {

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC

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
            setVoltage(allDAC[PIXEL+8*DEVICE], PIXEL, TCAADR_DAC[DEVICE], 0);
        }
    }

}

// set the DAC voltage output
void setVoltage(Adafruit_MCP4725 *dac,
                uint8_t PIXEL,
                uint8_t tcaADDR,
                float VOLTAGE_SET_VAL) {
    // for (int i = 0; i < 4; i++) {
    //     for (int j = 0; j < 8; j++) {
    TCA9548Access(PIXEL, tcaADDR);
    dac -> setVoltage(convert_to_12bit(VOLTAGE_SET_VAL), false);
        // }
    // }
}

// get new values from ina219
void getVolCurr(Adafruit_INA219 *ina219, uint8_t tcaADDR, uint8_t PIXEL) {
    TCA9548Access(PIXEL, tcaADDR);
    shuntvoltage       = ina219 -> getShuntVoltage_mV();
    busvoltage         = ina219 -> getBusVoltage_V();
    current_mA         = ina219 -> getCurrent_mA();
    power_mW           = ina219 -> getPower_mW();
    current_mA_Flipped = current_mA * -1;
    loadvoltage        = busvoltage + (shuntvoltage / 1000);
}

// TODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODOTODO
void lightControl(int light_Status) {
    if (light_Status == 0) {
        Serial.println("turned light off");
    } else if (light_Status == 1) {
        Serial.println("turned light on");
    }

}



