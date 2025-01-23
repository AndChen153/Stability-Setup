// serial_comm.cpp
#include "../include/serial_com.h"

extern char received_chars[];
extern char temp_chars[];
extern char mode_from_pc[];

extern float val1;
extern float val2;
extern int val3;
extern int val4;
extern int val5;

extern bool scan_done;
extern bool pno_done;
extern bool constant_voltage_done;

extern bool measurement_running;

/**
 * @brief Reads and processes serial data delimited by start and end markers.
 *
 * This function continuously checks for incoming serial data and processes it
 * if available. Data collection starts when the `startMarker` ('<') is detected
 * and continues until the `endMarker` ('>') is found. The received data is stored
 * in `received_chars`, and the string is terminated with a null character (`\0`)
 * once the `endMarker` is reached. It ensures that the received data does not
 * exceed the buffer size defined by `num_chars`.
 */
/**
serialCommResult recvWithStartEndMarkers()
{
    static bool recvInProgress = false;
    static byte ndx = 0;
    bool valuesRead = false;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0)
    {
        rc = Serial.read();
        Serial.print("Received char: ");
        Serial.println(rc);

        if (recvInProgress)
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
                valuesRead = true;
                ndx = 0;
                Serial.println("End marker received.");
            }
        }
        else if (rc == startMarker)
        {
            recvInProgress = true;
            Serial.println("Start marker received.");
        }
    }
    // clearSerialBuffer();

    strcpy(temp_chars, received_chars);
    Serial.println(temp_chars);
    parse_data();

    if (checkForStopMessage())
    {
        Serial.println("STOPPED");

        return serialCommResult::STOP;
    }
    // else if (valuesRead && measurement_running && check_valid_mode())
    else if (valuesRead && !measurement_running)
    {
        Serial.print("recvWithEndMarkers: ");
        show_parsed_data();
        Serial.println(temp_chars);

        return serialCommResult::START;
    }

    // memset(received_chars, '\0', num_chars);
    return serialCommResult::NONE;
}*/

serialCommResult recvWithLineTermination()
{
    if (Serial.available() > 0)
    {
        // Read the incoming string until newline
        String incomingString = Serial.readStringUntil('\n');
        incomingString.trim(); // Remove any leading/trailing whitespace

        Serial.print("Received string: ");
        Serial.println(incomingString);

        // Copy the string to received_chars buffer
        incomingString.toCharArray(received_chars, num_chars);

        // Copy to temp_chars for parsing
        strcpy(temp_chars, received_chars);

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

        // If measurement is not running and values have been read
        if (!measurement_running)
        {
            Serial.print("recvWithLineTermination: ");
            show_parsed_data();
            Serial.println(temp_chars);
            return serialCommResult::START;
        }
    }

    return serialCommResult::NONE;
}

/**
 * @brief Displays the parsed data via serial output.
 *
 * This function prints the parsed values (`val1`, `val2`, `val3`, `val4`, and `val5`)
 * to the serial monitor in a formatted manner for debugging or monitoring purposes.
 */
void show_parsed_data()
{
    Serial.print("Mode: ");
    Serial.print(mode_from_pc);
    Serial.print(", Val1: ");
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

// bool check_valid_mode()
// {
//     for (const String &mode : Modes)
//     {
//         if (String(mode_from_pc).equals(mode))
//         {
//             return true;
//         }
//     }
//     return false;
// }
