// version 1.2
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

/* Assign a unique ID to this sensor at the same time */
Adafruit_INA219 ina219_0;
Adafruit_INA219 ina219_1;
Adafruit_INA219 ina219_2;
Adafruit_INA219 ina219_3;
Adafruit_INA219 ina219_4;
Adafruit_INA219 ina219_5;
Adafruit_INA219 ina219_6;
Adafruit_INA219 ina219_7;
Adafruit_INA219 allINA219[] = {ina219_0, ina219_1, ina219_2, ina219_3, ina219_4, ina219_5, ina219_6, ina219_7};

Adafruit_MCP4725 dac_0;
Adafruit_MCP4725 dac_1;
Adafruit_MCP4725 dac_2;
Adafruit_MCP4725 dac_3;
Adafruit_MCP4725 dac_4;
Adafruit_MCP4725 dac_5;
Adafruit_MCP4725 dac_6;
Adafruit_MCP4725 dac_7;
Adafruit_MCP4725 allDAC[] = {dac_0, dac_1, dac_2, dac_3, dac_4, dac_5, dac_6, dac_7};

int TCAADR_INA[] = {0x70, 0x72, 0x74, 0x76};    // 112, 114, 116, 118
int TCAADR_DAC[] = {0x71, 0x73, 0x75, 0x77};    // 113, 115, 117, 119

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

      // variables to hold the parsed data
char messageFromPC[numChars] = {0};
boolean newData = false;

// Perturb and Observe  Variables -------------------------------------------------------
boolean perturb_And_ObserveDone = true;
float voltage_Starting_PnO      = 0.0;
float voltage_Step__Size_PnO    = 0.000;
int measurement_Delay_PnO       = 0;
int measurements_Per_Step_PnO   = 0;
unsigned long measurement_Time            = 0;
int dummy;

// Tracking and Scanning Variables ------------------------------------------------------
boolean tracking_And_ScanningDone = true;

float voltage_Starting_TaS    = 0.0;
float voltage_Step__Size_TaS  = 0.000;
int measurement_Delay_TaS     = 0;
int measurements_Per_Step_TaS = 0;

// Scan Variables -----------------------------------------------------------------------
boolean scanDone = true;

float avgVolt[8];
float avgCurr[8];
int volt_Step_Count = 0;
float voltage_val   = 0;
uint16_t dac_val    = 0;

float voltage_Range_Scan       = 0.0;
float voltage_Step_Size_Scan   = 0.000;
int measurements_Per_Step_Scan = 0;
int measurement_Rate_Scan     = 0;
int light_Status = 0;



// --------------------------------------------------------------------------------------


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

    Serial.begin(115200);
    while (!Serial)
    {
        delay(10);
    }
    Serial.println("ArduinoAuto8Pixels Test");

    // initialize sensors
    for (uint8_t ID = 0; ID < 8; ID ++) {
        // Serial.println(ID);
        setupSensor_INA219(&allINA219[ID], ID);
    }

    for (uint8_t ID = 0; ID < 8; ID ++) {
        // Serial.println(ID);
        setupSensor_Dac(&allDAC[ID], ID);
    }

    Serial.println("");
    Serial.println("setup completed");
}

void loop(void) {
    recvWithStartEndMarkers();
    if (newData == true && scanDone && tracking_And_ScanningDone) {
        strcpy(tempChars, receivedChars);
        parseData();
        showParsedData();
        zero();

        newData = false;
        String mode = String(messageFromPC);

        if (mode.equals("scan")) {
            scanDone = false;
        } else if (mode.equals("TaS")) {
            tracking_And_ScanningDone = false;
        } else if (mode.equals("PnO")) {
            perturb_And_ObserveDone = false;
        }
    }

    // scanDone = false;

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

    } else if (!tracking_And_ScanningDone) {
        Serial.println("Tracking and Scanning");

        voltage_Starting_TaS = val1;
        voltage_Step__Size_TaS = val2;
        measurement_Delay_TaS = val3;
        measurements_Per_Step_TaS = val4;
        dummy = val5;

        trackingAndScanning();
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

// --------------------------------------------------------------------------------------

void perturbAndObserve() {
    led(true);
    lightControl(1);

    float Vset[8];
    float VsetUp;
    float VsetDown;
    float time;

    int count;

    for (int ID = 0; ID < 8; ID ++) {
        Vset[ID] = voltage_Starting_PnO;
    }

    float avgPowerCalced[8];
    float avgPowerCalcedUp;
    float avgPowerCalcedDown;
    float loadvoltageArr[8];
    float current_mA_FlippedArr[8];
    float PCE[8];
    measurements_Per_Step_PnO++; //average not working correctly

    int currentMillis = 0;
    int pm = millis();
    int startMillis = millis();
    Serial.println(measurement_Time);
    measurement_Time *= 60;
    Serial.print("measurement_Time (sec): ");
    Serial.println(measurement_Time);
    while((millis()-startMillis)/1000.0 < measurement_Time) {
        //measurements_Per_Step_PnO


        for (int ID = 0; ID < 8; ++ID) {
            // Vset ---------------------------------------------------
            setVoltage(&allDAC[ID],  Vset[ID], ID);
            delay(measurement_Delay_PnO);

            for (int i = 0; i < measurements_Per_Step_PnO; ++i) {
                getINA129(&allINA219[ID], ID);
                avgPowerCalced[ID] += loadvoltage * current_mA_Flipped;
                loadvoltageArr[ID] += loadvoltage;
                current_mA_FlippedArr[ID] += current_mA_Flipped;
            }

            // Vset + deltaV ------------------------------------------
            VsetUp = Vset[ID] + voltage_Step__Size_PnO;
            setVoltage(&allDAC[ID],  VsetUp, ID);
            delay(measurement_Delay_PnO);

            for (int i = 0; i < measurements_Per_Step_PnO; ++i) {
                getINA129(&allINA219[ID], ID);
                avgPowerCalcedUp += loadvoltage * current_mA_Flipped;
            }
            // zero();

            // Vset - deltaV ------------------------------------------
            VsetDown = Vset[ID] - voltage_Step__Size_PnO;
            setVoltage(&allDAC[ID],  VsetDown, ID);
            delay(measurement_Delay_PnO);

            for (int i = 0; i < measurements_Per_Step_PnO; ++i) {
                getINA129(&allINA219[ID], ID);
                avgPowerCalcedDown += loadvoltage * current_mA_Flipped;
            }
            // zero();
            avgPowerCalced[ID] = avgPowerCalced[ID]/measurements_Per_Step_PnO;
            avgPowerCalcedUp = avgPowerCalcedUp/measurements_Per_Step_PnO;
            avgPowerCalcedDown = avgPowerCalcedDown/measurements_Per_Step_PnO;
            loadvoltageArr[ID] = loadvoltageArr[ID]/measurements_Per_Step_PnO;
            current_mA_FlippedArr[ID] = current_mA_FlippedArr[ID]/measurements_Per_Step_PnO;

            if (avgPowerCalcedUp > avgPowerCalcedDown && avgPowerCalcedUp > avgPowerCalced[ID]) {
                Vset[ID] += voltage_Step__Size_PnO;
            } else if (avgPowerCalcedDown > avgPowerCalcedUp && avgPowerCalcedDown > avgPowerCalced[ID]) {
                Vset[ID] -= voltage_Step__Size_PnO;
            }

            PCE[ID] = (avgPowerCalced[ID]/1000)/(0.1*0.128);
        }

        currentMillis = currentMillis + millis() - pm;
        pm = millis();
        Serial.print((millis()-startMillis)/1000.0, 4);
        Serial.print(", ");
        for (int ID = 0; ID < 8; ++ID) {
            Serial.print(loadvoltageArr[ID], 2);
            Serial.print(", ");
            Serial.print(current_mA_FlippedArr[ID], 2);
            Serial.print(", ");
        }

        for (int ID = 0; ID < 8; ++ID) {
            // Serial.print(loadvoltage, 4);
            // Serial.print(", ");
            // Serial.print(current_mA_Flipped, 4);
            // Serial.print(", ");
            Serial.print((PCE[ID]*100), 4);
            Serial.print(", ");
            // Serial.print(avgPowerCalcedUp, 4);
            // Serial.print(", ");
            // Serial.print(avgPowerCalced[ID], 4);
            // Serial.print(", ");
            // Serial.print(avgPowerCalcedDown, 4);
        }
        Serial.print(1);

        Serial.println("");
    }


    perturb_And_ObserveDone = true;
    led(false);

}

// --------------------------------------------------------------------------------------

void trackingAndScanning() {
    float Vset = voltage_Starting_TaS;
    float voltage_Step__Size_TaS = 0.000;
    int measurement_Delay_TaS = 0;
    int measurements_Per_Step_TaS = 0;

    dac_0.setVoltage(convert_to_12bit(voltage_Starting_TaS), false);
    delay(measurement_Delay_TaS);
    // to be implemented

}

// --------------------------------------------------------------------------------------

// performs forward or backward JV scan of solar cell
void scan(String dir) {
    led(true);


    int s = (voltage_Range_Scan*1000)/measurement_Rate_Scan;
    int steps = (voltage_Range_Scan*1000)/(voltage_Step_Size_Scan*1000);
    // Serial.print(s); Serial.print(" "); Serial.println (steps);


    // amount of time it takes to take measurement from all 8 ina219 on ARDUINO UNO
    // must change this on different setup
    int OFFSET = 35;

    int delayTimeMS = (s*1000)/steps - (OFFSET * measurements_Per_Step_Scan);
    if (delayTimeMS < 0) {delayTimeMS = 0;}

    Serial.print("started scan with delay time: "); Serial.println(delayTimeMS);

    float upperLimit;
    if (dir == "backward") {
        voltage_val = voltage_Range_Scan + voltage_Step_Size_Scan;
        upperLimit = voltage_Range_Scan + voltage_Step_Size_Scan;
    } else if (dir == "forward") {
        voltage_val = 0;
        upperLimit = voltage_Range_Scan - voltage_Step_Size_Scan;
    }

    for (int ID = 0; ID < 8; ++ID) {
        setVoltage(&allDAC[ID], voltage_val, ID);
    }

    delay(delayTimeMS);
    unsigned long startMillis = millis();

    while (upperLimit >= voltage_val && voltage_val >= 0) {
        // Serial.print(millis()); Serial.print(" "); Serial.println(volt_Step_Count); // used to measure offset
        if (volt_Step_Count > measurements_Per_Step_Scan) {
            if (dir == "backward") {
                voltage_val -= voltage_Step_Size_Scan;
            } else if (dir == "forward") {
                voltage_val += voltage_Step_Size_Scan;
            }

            for (int ID = 0; ID < 8; ID ++) {
                setVoltage(&allDAC[ID], voltage_val, ID);
            }


            delay(delayTimeMS);                    //to set the scan rate
            unsigned long currMillis = millis() - startMillis;

            Serial.print(currMillis/1000.0, 4);
            Serial.print(",");
            Serial.print(voltage_val);
            Serial.print(",");
            for (int ID = 0; ID < 8; ++ID) {
                Serial.print(avgVolt[ID]/volt_Step_Count, 4);
                Serial.print(",");
                Serial.print(avgCurr[ID]/volt_Step_Count, 4);
                Serial.print(",");
            }
            Serial.print(1);
            Serial.println("");
            // Serial.println("");

            // reset all values in array to 0
            memset(avgVolt, 0.0, sizeof(avgVolt));
            memset(avgCurr, 0.0, sizeof(avgCurr));
            volt_Step_Count = 0;
        } else {
            for (int ID = 0; ID < 8; ++ID) {
                getINA129(&allINA219[ID], ID);
                avgVolt[ID] += loadvoltage;
                avgCurr[ID] += current_mA_Flipped;
            }
            volt_Step_Count++;



        }
    }

    scanDone = true;
    led(false);
}

// --------------------------------------------------------------------------------------



// Helper functions ---------------------------------------------------------------------

// TO IMPLEMENT LATER
// TO IMPLEMENT LATER
// TO IMPLEMENT LATER
// TO IMPLEMENT LATER
void lightControl(int light_Status) {
    if (light_Status == 0) {
        Serial.println("turn light off");
    } else if (light_Status == 1) {
        Serial.println("turn light on");
    }

}

void displaySensorVals(Adafruit_INA219 *ina219, int ID) {
    TCA9548A_INA219(ID);
    Serial.println("------------------------------------");
    Serial.print("Sensor:     "); Serial.println(ID);
    Serial.print("Voltage:    "); Serial.println(ina219->getBusVoltage_V());
    Serial.print("Current:    "); Serial.println(ina219->getCurrent_mA());
    Serial.println("------------------------------------");
    Serial.println("");
    delay(500);
}

// --------------------------------------------------------------------------------------

void setupSensor_INA219(Adafruit_INA219 *ina219, uint8_t ID) {
    // Serial.print("ina219 setup started");
    TCA9548A_INA219(ID);
    if (!ina219->begin())
    {
        Serial.print("ina219_");
        Serial.print(ID);
        Serial.print(" not detected");
        // creates endless loop to stop program
        while (1);
    }
    ina219->setCalibration_16V_400mA();
    // Serial.print("INA219_"); Serial.print(ID); Serial.println(" is setup");
}

// --------------------------------------------------------------------------------------

void setupSensor_Dac(Adafruit_MCP4725 *dac, uint8_t ID) {
    // Serial.print("mcp4725 setup started");
    TCA9548A_MCP475(ID);
    if (!dac->begin())
    {
        Serial.print("dac_");
        Serial.print(ID);
        Serial.print(" not detected");
        // creates endless loop to stop program
        while (1);
    }
    // Serial.print("INA219_"); Serial.print(ID); Serial.println(" is setup");

}

// --------------------------------------------------------------------------------------

void TCA9548A_INA219(uint8_t bus) {
    // Serial.print("TCA channel "); Serial.print(bus); Serial.println(" activated");
    Wire.beginTransmission(0x70); // TCA9548A_INA219 address is 0x70
    Wire.write(1 << bus);         // send byte to select bus
    Wire.endTransmission();

}

// --------------------------------------------------------------------------------------

void TCA9548A_MCP475(uint8_t bus) {
    Wire.beginTransmission(0x71); // TCA9548A_MCP475 address is 0x71

    Wire.write(1 << bus);         // send byte to select bus
    Wire.endTransmission();
    // Serial.print("TCA channel "); Serial.print(bus); Serial.println(" activated");
}

// --------------------------------------------------------------------------------------

// for receiving data values over serial
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

// --------------------------------------------------------------------------------------

// update ina219 values
void getINA129(Adafruit_INA219 *ina219, uint8_t ID) {
    TCA9548A_INA219(ID);
    shuntvoltage       = ina219 -> getShuntVoltage_mV();
    busvoltage         = ina219 -> getBusVoltage_V();
    current_mA         = ina219 -> getCurrent_mA();
    power_mW           = ina219 -> getPower_mW();
    current_mA_Flipped = current_mA * -1;
    loadvoltage        = busvoltage + (shuntvoltage / 1000);
}

// --------------------------------------------------------------------------------------


// set the DAC voltage out
void setVoltage(Adafruit_MCP4725 *dac, float voltage_val, uint8_t ID) {
    TCA9548A_MCP475(ID);
    dac -> setVoltage(convert_to_12bit(voltage_val), false);
}

// --------------------------------------------------------------------------------------

// zeros the MCP4725
void zero() {
    for (int ID = 0; ID < 8; ID ++) {
        setVoltage(&allDAC[ID], 0, ID);
    }
    delay(30);
}

// --------------------------------------------------------------------------------------

// convert decimal voltage value to 12 bit int to control the MCP4725
uint16_t convert_to_12bit(float val) {
    if (val < 0 or val > 3.3) {
        return 0;
    }
    val = float(val)*4095.0/3.3;
    int bits = floor(val);
    return bits;
}

// --------------------------------------------------------------------------------------

// splitting the data received over serial into variables
void parseData() {      // split the data into its parts

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

// --------------------------------------------------------------------------------------

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

// --------------------------------------------------------------------------------------

void led(boolean status) {
    if (status) {
        digitalWrite(LED_BUILTIN, HIGH);
    } else {
        digitalWrite(LED_BUILTIN, LOW);
    }
}