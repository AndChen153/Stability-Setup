// serial_comm.cpp
#include "../include/serial_com.h"

// extern const byte num_chars;
extern char received_chars[];
extern char temp_chars[];
extern char mode_from_pc[];
extern boolean new_data;

extern float val1;
extern float val2;
extern int val3;
extern int val4;
extern int val5;

void recvWithStartEndMarkers()
{
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && new_data == false)
    {
        rc = Serial.read();

        if (recvInProgress == true)
        {
            if (rc != endMarker)
            {
                received_chars[ndx] = rc;
                ndx++;
                if (ndx >= num_chars)
                {
                    ndx = num_chars - 1;
                }
            }
            else
            {
                received_chars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                new_data = true;
            }
        }
        else if (rc == startMarker)
        {
            recvInProgress = true;
        }
    }
}

void parse_data()
{
    char *strtokIndx;

    strtokIndx = strtok(temp_chars, ",");
    strcpy(mode_from_pc, strtokIndx);

    strtokIndx = strtok(NULL, ",");
    val1 = atof(strtokIndx);

    strtokIndx = strtok(NULL, ",");
    val2 = atof(strtokIndx);

    strtokIndx = strtok(NULL, ",");
    val3 = atoi(strtokIndx);

    strtokIndx = strtok(NULL, ",");
    val4 = atoi(strtokIndx);

    strtokIndx = strtok(NULL, ",");
    val5 = atoi(strtokIndx);
}

void show_parsed_data()
{
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
