// serial_comm.cpp
#include "../include/serial_com.h"

extern char received_chars[];
extern char temp_chars[];
extern char mode_from_pc[];

extern float val1;
extern float val2;
extern float val3;
extern int val4;
extern int val5;
extern int val6;

extern bool scan_done;
extern bool mppt_done;
extern bool constant_voltage_done;

extern bool measurement_running;

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

        char *token = strtok(temp_chars, ",");
        // Parse mode (a string)
        if (token != NULL) {
            strcpy(mode_from_pc, token);
        } else {
            mode_from_pc[0] = '\0'; // Default to an empty string if missing
        }

        // Parse val1 (float)
        token = strtok(NULL, ",");
        val1 = (token != NULL) ? atof(token) : 0;

        // Parse val2 (float)
        token = strtok(NULL, ",");
        val2 = (token != NULL) ? atof(token) : 0;

        // Parse val3 (float)
        token = strtok(NULL, ",");
        val3 = (token != NULL) ? atof(token) : 0;

        // Parse val4 (int)
        token = strtok(NULL, ",");
        val4 = (token != NULL) ? atoi(token) : 0;

        // Parse val5 (int)
        token = strtok(NULL, ",");
        val5 = (token != NULL) ? atoi(token) : 0;

        // Parse val6 (int)
        token = strtok(NULL, ",");
        val6 = (token != NULL) ? atoi(token) : 0;

        // If measurement is not running and values have been read
        if (!measurement_running)
        {
            Serial.print("Recieved Params: ");
            showParsedData();
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
void showParsedData()
{
    Serial.print("Mode: ");
    Serial.print(mode_from_pc);
    Serial.print(", Val1: ");
    Serial.print(val1, 4);
    Serial.print(", Val2: ");
    Serial.print(val2, 4);
    Serial.print(", Val3: ");
    Serial.print(val3, 4);
    Serial.print(", Val4: ");
    Serial.print(val4);
    Serial.print(", Val5: ");
    Serial.print(val5);
    Serial.print(", Val6: ");
    Serial.print(val6);
    Serial.println("");
}
