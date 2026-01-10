// serial_comm.cpp
#include "../include/serial_com.h"

extern char received_chars[NUM_CHARS];
extern char str_param[MAX_MODE_LEN];
extern char mode[MAX_MODE_LEN];

extern float vset[8];
extern float mppt_step_size_V;
extern int mppt_measurements_per_step;
extern int mppt_delay;
extern int mppt_measurement_interval;
extern unsigned long mppt_time_mins;

extern float scan_range;
extern float scan_step_size;
extern int scan_read_count;
extern int scan_rate;
extern int light_status;

extern volatile bool scan_done;
extern volatile bool mppt_done;

extern volatile bool measurement_running;
volatile bool done_recv = false;
volatile bool mode_received = false;

serialCommResult recvWithLineTermination()
{

    serialCommResult result = serialCommResult::NONE;
    while (Serial.available() > 0 && !done_recv)
    {
        // Read the incoming string until newline
        String incomingString = Serial.readStringUntil('\n');
        // Serial.print(F("Received line (before error check): ");
        // Serial.println(F(incomingString));

        incomingString.trim(); // Remove any leading/trailing whitespace
        // Check if the trimmed string will fit in the buffer
        if (incomingString.length() >= NUM_CHARS)
        {
            Serial.print(F("Error: Received line too long (max "));
            Serial.print(NUM_CHARS - 1); // num_chars includes space for null terminator
            Serial.println(F(" characters). Skipping."));
            continue; // Skip this line and check for the next one
        }

        // Copy the string to received_chars buffer
        incomingString.toCharArray(received_chars, NUM_CHARS);

        Serial.print(F("Received line: "));
        Serial.println(received_chars); // Print the buffer content


        char *param = strtok(received_chars, ",");
        if (param == NULL)
        {
            Serial.println(F("Warning: Received empty or invalid line after trimming."));
            continue;
        }

        strncpy(str_param, param, MAX_MODE_LEN - 1);
        // Ensure null termination in case the token was longer than MAX_MODE_LEN - 1
        str_param[MAX_MODE_LEN - 1] = '\0';

        if (!mode_received)
        {
            if (strcmp(str_param, "scan") == 0 || strcmp(str_param, "mppt") == 0)
            {
                Serial.print(F("Mode Received: "));
                Serial.println(str_param);
                mode_received = true;
                strncpy(mode, str_param, MAX_MODE_LEN - 1);
            }
            else
            {
                Serial.print(F("Warning: Expected 'scan' or 'mppt' mode, but received '"));
                Serial.print(str_param);
                Serial.println(F("'. Ignoring line."));
                continue;
            }
        }
        else if (strcmp(str_param, "done") == 0)
        {
            Serial.println(F("'done' command received."));
            done_recv = true;
        }
        else if (strcmp(mode, "scan") == 0)
        {
            param = strtok(NULL, ",");
            if (param == NULL) {
                Serial.println(F("Warning: Missing value for scan parameter."));
                continue;
            }
            if (strcmp(str_param, "1") == 0)
            {
                scan_range = atof(param);
            }
            else if (strcmp(str_param, "2") == 0)
            {
                scan_step_size = atof(param);
            }
            else if (strcmp(str_param, "3") == 0)
            {
                scan_read_count = atoi(param);
            }
            else if (strcmp(str_param, "4") == 0)
            {
                scan_rate = atoi(param);
            }
            else if (strcmp(str_param, "5") == 0)
            {
                light_status = atoi(param);
            }
            else {
                Serial.print(F("Warning: Unknown scan parameter identifier "));
                Serial.print(str_param);
                Serial.println(F("'. Ignoring line."));
           }
        }
        else if (strcmp(mode, "mppt") == 0)
        {
            if (strcmp(str_param, "1") == 0) // vset[8]
            {
                for (uint8_t ID = 0; ID < 8; ID++)
                {
                    param = strtok(NULL, ","); // Get the next Vset value
                    if (param != NULL) {
                        vset[ID] = atof(param);
                    } else {
                        // Handle case where not enough vset values are provided
                        Serial.print(F("Warning: Missing vset value(s) from ID "));
                        Serial.println(ID);
                        // Fill rest of vset
                        for (uint8_t j = ID; j < 8; j++) vset[j] = 0;
                        break;
                    }
                }
            }
            else
            {
                // Single value parameters
                param = strtok(NULL, ",");
                if (param == NULL) {
                    Serial.println(F("Warning: Missing value for MPPT parameter."));
                    continue;
                }

                if (strcmp(str_param, "2") == 0)
                {
                    mppt_step_size_V = atof(param);
                }
                else if (strcmp(str_param, "3") == 0)
                {
                    mppt_time_mins = atoi(param);
                }
                else if (strcmp(str_param, "4") == 0)
                {
                    mppt_measurements_per_step = atoi(param);
                }
                else if (strcmp(str_param, "5") == 0)
                {
                    mppt_delay = atoi(param);
                }
                else if (strcmp(str_param, "6") == 0)
                {
                    mppt_measurement_interval = atoi(param);
                }
                else {
                    Serial.print(F("Warning: Unknown MPPT parameter identifier '"));
                    Serial.print(str_param);
                    Serial.println(F("'. Ignoring line."));
                }
            }
        }
        // If measurement is not running and values have been read
        if (done_recv) {
            if (!measurement_running)
            {
                Serial.println(F("Parameters successfully received and parsed."));
                showParsedData();
                result = serialCommResult::START;
            } else {
                // Measurement already running
                Serial.println(F("Warning: Received 'done' command while measurement is already running."));
                result = serialCommResult::NONE;
            }
        }
    }

    return result;
}

/**
 * @brief Displays the parsed data via serial output.
 */
void showParsedData()
{

    if (strcmp(mode, "mppt") == 0) {
        Serial.print(F("Mode: "));
        Serial.print(mode);
        Serial.print(F(", Vset: ["));
        for (int i = 0; i < 8; i++) // Use constant here
        {
            Serial.print(vset[i], 4); // Print with precision
            if (i < 8 - 1) {
                Serial.print(F(", "));
            }
        }
        Serial.println(F("] "));
        Serial.print(F("mppt_step_size_V: "));
        Serial.println(mppt_step_size_V, 4);
        Serial.print(F("mppt_measurements_per_step: "));
        Serial.println(mppt_measurements_per_step);
        Serial.print(F("mppt_delay: "));
        Serial.println(mppt_delay);
        Serial.print(F("mppt_measurement_interval: "));
        Serial.println(mppt_measurement_interval);
        Serial.print(F("mppt_time_mins: "));
        Serial.println(mppt_time_mins);

    }
    else if (strcmp(mode, "scan") == 0) {
        Serial.print(F("Mode: "));
        Serial.println(mode);
        Serial.print("scan_range: ");
        Serial.println(scan_range, 4);
        Serial.print(F("scan_step_size: "));
        Serial.println(scan_step_size, 4);
        Serial.print(F("scan_read_count: "));
        Serial.println(scan_read_count);
        Serial.print(F("scan_rate: "));
        Serial.println(scan_rate);
        Serial.print(F("light_status: "));
        Serial.println(light_status);

    }
    Serial.println(F(""));
}
