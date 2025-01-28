// Example 5 - Receive with start- and end-markers combined with parsing
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac_A;
Adafruit_INA219 ina219_A;

float shuntvoltage_A = 0;
float busvoltage_A = 0;
float current_mA_A = 0;
float loadvoltage_A = 0;
float power_mW_A = 0;
float current_mA_A_Flipped = 0;

// Serial Input Variables
float val1;
float val2;
int val3;
int val4;
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

      // variables to hold the parsed data
char messageFromPC[numChars] = {0};
boolean newData = false;

// Perturb and Observe  Variables
boolean perturb_And_ObserveDone = true;
float voltage_Starting_PnO = 0.0;
float voltage_Step__Size_PnO = 0.000;
int measurement_Delay_PnO = 0;
int measurements_Per_Step_PnO = 0;

// Tracking and Scanning Variables
boolean tracking_And_ScanningDone = true;

float voltage_Starting_TaS = 0.0;
float voltage_Step__Size_TaS = 0.000;
int measurement_Delay_TaS = 0;
int measurements_Per_Step_TaS = 0;

// Scan Variables
boolean scanDone = true;

float avgVolt_A = 0.0;
float avgCurr_A = 0.0;
int volt_Step_Count = 0;
float voltage_val = 0;
uint16_t dac_val = 0;


float voltage_Range_Scan = 0.0;
float voltage_Step_Size_Scan = 0.000;
int measurements_Per_Step_Scan = 0;
int measurement_Delay_Scan = 0;


//============

void setup() {
    Serial.begin(115200);
    Serial.println("started");

    while (!Serial)
    {
        // will pause Zero, Leonardo, etc until serial console opens
        delay(1);
    }
    if (!ina219_A.begin())
    {
        Serial.println("Failed to find ina219_A chip");
        while (1)
        {
            delay(10);
        }
    }
    if (!dac_A.begin())
    {
        Serial.println("Failed to find dac_A chip");
        while (1)
        {
            delay(10);
        }
    }
    ina219_A.setCalibration_16V_400mA();
}

void loop() {
    recvWithStartEndMarkers();
    if (newData == true && scanDone && tracking_And_ScanningDone) {
        strcpy(tempChars, receivedChars);
        parseData();
        // showParsedData();
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

    if (!scanDone) {
        Serial.println("Scanning");
        voltage_Range_Scan = val1;
        voltage_Step_Size_Scan = val2;
        measurements_Per_Step_Scan = val3;
        measurement_Delay_Scan = val4;
        scan("backward");
        scan("forward");
        scanDone = true;
        Serial.print("Done!");
    } else if (!tracking_And_ScanningDone) {
        Serial.println("TaS");
        voltage_Starting_TaS = val1;
        voltage_Step__Size_TaS = val2;
        measurement_Delay_TaS = val3;
        measurements_Per_Step_TaS = val4;
        trackingAndScanning();
        Serial.print("Done!");
    } else if (!perturb_And_ObserveDone) {
        Serial.println("PnO");
        voltage_Starting_PnO = val1;
        voltage_Step__Size_PnO = val2;
        measurements_Per_Step_PnO= val3;
        measurement_Delay_PnO = val4;
        perturbAndObserve();
        Serial.print("Done!");
    }
}

void perturbAndObserve() {
    float Vset = voltage_Starting_PnO;
    float VsetUp;
    float VsetDown;

    int count;
    float avgPowerCalced = 0;
    float avgPowerCalcedUp = 0;
    float avgPowerCalcedDown = 0;
    float PCE = 0;


    while(millis()/1000 < 120) {
        avgPowerCalced = 0;
        avgPowerCalcedUp = 0;
        avgPowerCalcedDown = 0;


        // Vset ---------------------------------------------------
        dac_A.setVoltage(convert_to_12bit(Vset), false);
        delay(measurement_Delay_PnO*10);
        for (count = 0; count < measurements_Per_Step_PnO; count++) {
            dac_A.setVoltage(convert_to_12bit(Vset), false);

            getINA129_A();
            // Serial.print(Vset);
            // Serial.print(", ");
            // Serial.print(loadvoltage_A, 4);
            // Serial.print(", ");
            // Serial.print(current_mA_A_Flipped, 4);
            // Serial.print(", ");
            // Serial.print(abs(loadvoltage_A * current_mA_A), 4);
            // Serial.print(", ");
            // Serial.print(millis()/1000.0, 4);
            // Serial.println("");

            avgPowerCalced += abs(loadvoltage_A * current_mA_A);
            delay (measurement_Delay_PnO);
        }
        avgPowerCalced = avgPowerCalced/count;
        // Serial.print("avg power calced: ");
        // Serial.println(avgPowerCalced);

        zero();
        delay(measurement_Delay_PnO);


        // Vset + deltaV ------------------------------------------
        VsetUp = Vset + voltage_Step__Size_PnO;
        dac_A.setVoltage(convert_to_12bit(VsetUp), false);
        delay(measurement_Delay_PnO*10);

        for (count = 0; count < measurements_Per_Step_PnO; count++) {
            dac_A.setVoltage(convert_to_12bit(VsetUp), false);

            getINA129_A();

            avgPowerCalcedUp += abs(loadvoltage_A * current_mA_A);
            delay (measurement_Delay_PnO);
        }
        avgPowerCalcedUp = avgPowerCalcedUp/count;

        zero();
        delay(measurement_Delay_PnO);


        // Vset - deltaV ------------------------------------------
        VsetDown = Vset - voltage_Step__Size_PnO;
        dac_A.setVoltage(convert_to_12bit(VsetDown), false);
        delay(measurement_Delay_PnO*10);

        for (count = 0; count < measurements_Per_Step_PnO; count++) {
            dac_A.setVoltage(convert_to_12bit(VsetDown), false);

            getINA129_A();

            avgPowerCalcedDown += abs(loadvoltage_A * current_mA_A);
            delay (measurement_Delay_PnO);
        }
        avgPowerCalcedDown = avgPowerCalcedDown/count;


        if (avgPowerCalcedUp > avgPowerCalcedDown && avgPowerCalcedUp > avgPowerCalced) {
            Vset += voltage_Step__Size_PnO/3;
        } else if (avgPowerCalcedDown > avgPowerCalcedUp && avgPowerCalcedDown > avgPowerCalced) {
            Vset -= voltage_Step__Size_PnO/3;
        }

        PCE = (avgPowerCalced/1000)/(0.1*0.128);

        Serial.print(Vset);
        Serial.print(", ");
        Serial.print(loadvoltage_A, 4);
        Serial.print(", ");
        Serial.print(current_mA_A_Flipped, 4);
        Serial.print(", ");
        Serial.print(PCE, 4);
        Serial.print(", ");
        Serial.print(millis()/1000.0, 4);
        Serial.println("");
    }

    perturb_And_ObserveDone = true;

}

void trackingAndScanning() {
    float Vset = voltage_Starting_TaS;
    float voltage_Step__Size_TaS = 0.000;
    int measurement_Delay_TaS = 0;
    int measurements_Per_Step_TaS = 0;

    dac_A.setVoltage(convert_to_12bit(voltage_Starting_TaS), false);
    delay(measurement_Delay_TaS);

}

// zeros the MCP4725
void zero() {
    for (int i = 0; i < 10; i++) {
        dac_A.setVoltage(0, false);
    }
    delay(10);
}

// performs forward or backward JV scan of solar cell
void scan(String dir) {
    float upperLimit;
    if (dir == "backward") {
        voltage_val = voltage_Range_Scan + voltage_Step_Size_Scan;
        upperLimit = voltage_Range_Scan + voltage_Step_Size_Scan;
    } else if (dir == "forward") {
        voltage_val = 0;
        upperLimit = voltage_Range_Scan - voltage_Step_Size_Scan;
    }

    dac_A.setVoltage(convert_to_12bit(voltage_val), false);
    delay(50);


    while (upperLimit >= voltage_val && voltage_val >= 0) {
        if (volt_Step_Count > measurements_Per_Step_Scan) {
            if (dir == "backward") {
                voltage_val -= voltage_Step_Size_Scan;
            } else if (dir == "forward") {
                voltage_val += voltage_Step_Size_Scan;
            }
            dac_A.setVoltage(convert_to_12bit(voltage_val), false);
            delay(measurement_Delay_Scan);                    //settling time

            Serial.print(voltage_val);
            Serial.print(",");
            Serial.print(avgVolt_A/volt_Step_Count, 4);
            Serial.print(",");
            Serial.print(avgCurr_A/volt_Step_Count, 4);
            Serial.print(",");
            Serial.print(millis()/1000.0, 4);
            Serial.println("");


            avgVolt_A = 0;
            avgCurr_A = 0;
            volt_Step_Count = 0;
        } else {
            getINA129_A();
            // Serial.print(voltage_val);
            // Serial.print(",");
            // Serial.print(loadvoltage_A, 4);
            // Serial.print(",");
            // Serial.print(current_mA_A_Flipped, 4);
            // Serial.print(", ");
            // Serial.print(millis()/1000.0, 4);
            // Serial.println("");
            // Serial.println(loadvoltage_A);
            avgVolt_A += loadvoltage_A;
            avgCurr_A += current_mA_A_Flipped;
            volt_Step_Count++;
            delay(measurement_Delay_Scan);
        }
        delay(5);
    }

    scanDone = true;
}

void getINA129_A() {
    shuntvoltage_A = ina219_A.getShuntVoltage_mV();
    busvoltage_A = ina219_A.getBusVoltage_V();
    current_mA_A = ina219_A.getCurrent_mA();
    power_mW_A = ina219_A.getPower_mW();
    current_mA_A_Flipped = current_mA_A * -1;
    loadvoltage_A = busvoltage_A + (shuntvoltage_A / 1000);
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

// splitting the data received over serial into variables
void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC

    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    val1 = atof(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ",");
    val2 = atof(strtokIndx);     // convert this part to a float

    strtokIndx = strtok(NULL, ",");
    val3 = atoi(strtokIndx);     // convert this part to a float

    strtokIndx = strtok(NULL, ",");
    val4 = atoi(strtokIndx);     // convert this part to a float

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
    Serial.println("");
}