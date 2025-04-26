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
extern volatile bool constant_voltage_done;

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
        // Serial.print("Received line (before error check): ");
        // Serial.println(incomingString);

        incomingString.trim(); // Remove any leading/trailing whitespace
        // Check if the trimmed string will fit in the buffer
        if (incomingString.length() >= NUM_CHARS)
        {
            Serial.print("Error: Received line too long (max ");
            Serial.print(NUM_CHARS - 1); // num_chars includes space for null terminator
            Serial.println(" characters). Skipping.");
            continue; // Skip this line and check for the next one
        }

        // Copy the string to received_chars buffer
        incomingString.toCharArray(received_chars, NUM_CHARS);

        Serial.print("Received line: ");
        Serial.println(received_chars); // Print the buffer content


        char *param = strtok(received_chars, ",");
        if (param == NULL)
        {
            Serial.println("Warning: Received empty or invalid line after trimming.");
            continue;
        }

        strncpy(str_param, param, MAX_MODE_LEN - 1);
        // Ensure null termination in case the token was longer than MAX_MODE_LEN - 1
        str_param[MAX_MODE_LEN - 1] = '\0';

        if (!mode_received)
        {
            if (strcmp(str_param, "scan") == 0 || strcmp(str_param, "mppt") == 0)
            {
                Serial.print("Mode Received: ");
                Serial.println(str_param);
                mode_received = true;
                strncpy(mode, str_param, MAX_MODE_LEN - 1);
            }
            else
            {
                Serial.print("Warning: Expected 'scan' or 'mppt' mode, but received '");
                Serial.print(str_param);
                Serial.println("'. Ignoring line.");
                continue;
            }
        }
        else if (strcmp(str_param, "done") == 0)
        {
            Serial.println("'done' command received.");
            done_recv = true;
        }
        else if (strcmp(mode, "scan") == 0)
        {
            param = strtok(NULL, ",");
            if (param == NULL) {
                Serial.println("Warning: Missing value for scan parameter.");
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
                Serial.print("Warning: Unknown scan parameter identifier '");
                Serial.print(str_param);
                Serial.println("'. Ignoring line.");
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
                        Serial.print("Warning: Missing vset value(s) from ID ");
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
                    Serial.println("Warning: Missing value for MPPT parameter.");
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
                    Serial.print("Warning: Unknown MPPT parameter identifier '");
                    Serial.print(str_param);
                    Serial.println("'. Ignoring line.");
                }
            }
        }
        // If measurement is not running and values have been read
        if (done_recv) {
            if (!measurement_running)
            {
                Serial.println("Parameters successfully received and parsed.");
                showParsedData();
                result = serialCommResult::START;
            } else {
                // Measurement already running
                Serial.println("Warning: Received 'done' command while measurement is already running.");
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
        Serial.print("Mode: ");
        Serial.print(mode);
        Serial.print(", Vset: [");
        for (int i = 0; i < 8; i++) // Use constant here
        {
            Serial.print(vset[i], 4); // Print with precision
            if (i < 8 - 1) {
                Serial.print(", ");
            }
        }
        Serial.println("] ");
        Serial.print("mppt_step_size_V: ");
        Serial.println(mppt_step_size_V, 4);
        Serial.print("mppt_measurements_per_step: ");
        Serial.println(mppt_measurements_per_step);
        Serial.print("mppt_delay: ");
        Serial.println(mppt_delay);
        Serial.print("mppt_measurement_interval: ");
        Serial.println(mppt_measurement_interval);
        Serial.print("mppt_time_mins: ");
        Serial.println(mppt_time_mins);

    }
    else if (strcmp(mode, "scan") == 0) {
        Serial.print("Mode: ");
        Serial.println(mode);
        Serial.print("scan_range: ");
        Serial.println(scan_range, 4);
        Serial.print("scan_step_size: ");
        Serial.println(scan_step_size, 4);
        Serial.print("scan_read_count: ");
        Serial.println(scan_read_count);
        Serial.print("scan_rate: ");
        Serial.println(scan_rate);
        Serial.print("light_status: ");
        Serial.println(light_status);

    }
    Serial.println("");
}
