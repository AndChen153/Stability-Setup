#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac_A;
Adafruit_INA219 ina219_A;

uint16_t input;
String input_value;
int volts;
int count;
// float dacVoltsOut;

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

      // variables to hold the parsed data
char messageFromPC[numChars] = {0};
int integerFromPC = 0;
float floatFromPC = 0.0;

float voltage_Range = 0.0;
float voltage_Step_Size = 0.0;
int voltage_Read_Count = 0;


boolean newData = false;
boolean cycleDone = true;

void setup()
{
    Serial.begin(115200);
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

void loop()
{
    if (Serial.available())
    {
        input_value = Serial.readString();
        volts = input_value.toInt();
        if (volts > 0)
        {
            input = (uint16_t)volts;
        }
        else if (volts < 0)
        {
            input = 0;
        }

        count = 0;

        // if
        // if (input > 4095 or input < 0)
        // {
        //     input = 0;
        // }
    }

    float shuntvoltage_A = 0;
    float busvoltage_A = 0;
    float current_mA_A = 0;
    float loadvoltage_A = 0;
    float power_mW_A = 0;
    float current_mA_A_Flipped = 0;

    dac_A.setVoltage(input, false);
    float voltsOut = input/4096.0 * 3.3;

    shuntvoltage_A = ina219_A.getShuntVoltage_mV();
    busvoltage_A = ina219_A.getBusVoltage_V();
    current_mA_A = ina219_A.getCurrent_mA();
    current_mA_A_Flipped = current_mA_A * -1;
    power_mW_A = ina219_A.getPower_mW();
    loadvoltage_A = busvoltage_A + (shuntvoltage_A / 1000);

    if (count < 3 ) {
        Serial.print(loadvoltage_A);
        Serial.print(", ");
        Serial.print(current_mA_A_Flipped);

        Serial.println("");
        count++;
    }
    delay(10);
}

//============


// void recvWithStartEndMarkers() {
//     static boolean recvInProgress = false;
//     static byte ndx = 0;
//     char startMarker = '<';
//     char endMarker = '>';
//     char rc;

//     while (Serial.available() > 0 && newData == false) {
//         rc = Serial.read();

//         if (recvInProgress == true) {
//             if (rc != endMarker) {
//                 receivedChars[ndx] = rc;
//                 ndx++;
//                 if (ndx >= numChars) {
//                     ndx = numChars - 1;
//                 }
//             }
//             else {
//                 receivedChars[ndx] = '\0'; // terminate the string
//                 recvInProgress = false;
//                 ndx = 0;
//                 newData = true;
//             }
//         }

//         else if (rc == startMarker) {
//             recvInProgress = true;
//         }
//     }
// }


// //============

// void parseData() {      // split the data into its parts

//     char * strtokIndx; // this is used by strtok() as an index

//     strtokIndx = strtok(tempChars,",");      // get the first part - the string
//     strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC

//     strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
//     voltage_Range = atof(strtokIndx);     // convert this part to an integer

//     strtokIndx = strtok(NULL, ",");
//     voltage_Step_Size = atof(strtokIndx);     // convert this part to a float

//     strtokIndx = strtok(NULL, ",");
//     voltage_Read_Count = atof(strtokIndx);     // convert this part to a float

// }

// //============

// void showParsedData() {
//     Serial.print(messageFromPC);
//     Serial.print(",");
//     Serial.print(voltage_Range);
//     Serial.print(",");
//     Serial.print(voltage_Step_Size);
//     Serial.print(",");
//     Serial.print(voltage_Read_Count);
//     Serial.println(" ");
// }