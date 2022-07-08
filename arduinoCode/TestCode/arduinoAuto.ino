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

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

      // variables to hold the parsed data
char messageFromPC[numChars] = {0};
boolean newData = false;
boolean cycleDone = true;

float avgVolt_A = 0.0;
float avgCurr_A = 0.0;

int volt_Step_Count = 0;
float voltage_Range = 0.0;
float voltage_Step_Size = 0.000;
int voltage_Read_Count = 0;
float voltage_val = 0;
uint16_t dac_val = 0;

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

    // dacVoltsOut = 0.8;
    ina219_A.setCalibration_16V_400mA();
}

//============

void loop() {
    recvWithStartEndMarkers();
    if (newData == true && cycleDone) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
        // showParsedData();
        zero();
        newData = false;
        cycleDone = false;
    }
    if (cycleDone == false) {
        scan("backward");
        scan("forward");
        cycleDone = true;
        Serial.print("Done!");
    }
}

void zero() {
    for (int i = 0; i < 10; i++) {
        dac_A.setVoltage(0, false);
    }
    delay(10);
}

void scan(String dir) {
    float upperLimit;
    if (dir == "backward") {
        voltage_val = voltage_Range + voltage_Step_Size;
        upperLimit = voltage_Range + voltage_Step_Size;
    } else if (dir == "forward") {
        voltage_val = 0;
        upperLimit = voltage_Range - voltage_Step_Size;
    }

    dac_A.setVoltage(convert_to_12bit(voltage_val), false);

    while (upperLimit >= voltage_val && voltage_val >= 0) {
        if (volt_Step_Count > voltage_Read_Count) {
            if (dir == "backward") {
                voltage_val -= voltage_Step_Size;
            } else if (dir == "forward") {
                voltage_val += voltage_Step_Size;
            }
            dac_A.setVoltage(convert_to_12bit(voltage_val), false);
            delay(30);                          //settling time

            // Serial.print(voltage_val);
            // Serial.print(",");
            // Serial.print(avgVolt_A/volt_Step_Count, 4);
            // Serial.print(",");
            // Serial.print(avgCurr_A/volt_Step_Count, 4);
            // Serial.println("");

            avgVolt_A = 0;
            avgCurr_A = 0;
            volt_Step_Count = 0;
        } else {
            shuntvoltage_A = ina219_A.getShuntVoltage_mV();
            busvoltage_A = ina219_A.getBusVoltage_V();
            current_mA_A = ina219_A.getCurrent_mA();
            current_mA_A_Flipped = current_mA_A * -1;
            loadvoltage_A = busvoltage_A + (shuntvoltage_A / 1000);
            Serial.print(voltage_val);
            Serial.print(",");
            Serial.print(loadvoltage_A, 4);
            Serial.print(",");
            Serial.print(current_mA_A_Flipped, 4);
            Serial.println("");
            Serial.println(loadvoltage_A);
            avgVolt_A += loadvoltage_A;
            avgCurr_A += current_mA_A_Flipped;
            volt_Step_Count++;
        }
        delay(5);
    }
}

uint16_t convert_to_12bit(float val) {
    if (val < 0 or val > 3.3) {
        return 0;
    }
    val = float(val)*4095.0/3.3;
    int bits = floor(val);
    return bits;
}

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

//============

void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC

    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    voltage_Range = atof(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ",");
    voltage_Step_Size = atof(strtokIndx);     // convert this part to a float

    strtokIndx = strtok(NULL, ",");
    voltage_Read_Count = atoi(strtokIndx);     // convert this part to a float

}

//============

void showParsedData() {
    Serial.print("voltage_Range ");
    Serial.print(voltage_Range);
    Serial.print(", voltage_Step_Size ");
    Serial.print(voltage_Step_Size);
    Serial.print(", voltage_Read_Count ");
    Serial.print(voltage_Read_Count);
    Serial.println("");
}