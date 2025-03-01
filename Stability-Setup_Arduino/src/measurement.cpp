// measurement.cpp
#include "../include/measurement.h"
#include "../include/sensor.h"
#include "../include/serial_com.h"
#include "../include/helper.h"

// Extern variables from main
extern float vset[8];
extern bool mppt_done;
extern float voltage_starting_mppt;
extern float voltage_step_size_mppt;
extern int measurement_delay_mppt;
extern int measurements_per_step_mppt;
extern unsigned long measurement_time_mins_mppt;
extern float area_of_collector_mppt;

extern bool scan_done;
extern float avg_volt[8];
extern float avg_curr[8];
extern int volt_step_count;
extern float voltage_val;

extern float voltage_range_scan;
extern float voltage_step_size_scan;
extern int measurements_per_step_scan;
extern int measurement_rate_scan;
extern int light_status;

extern bool constant_voltage_done;
extern float constant_voltage;

extern float load_voltage;
extern float current_mA_Flipped;

extern uint32_t uniqueID;

const float measurement_time = 21;

void perturbAndObserveClassic()
{
    led(true);
    light_control(1);
    // Serial.println("")
    // TODO: use longer moving average or more complex filter
    float moving_average_n = 5;
    int count;
    float temp_voltage = 0.0;
    float temp_flipped_A = 0.0;
    float load_voltageArr[8];
    float current_mA_flipped_arr[8];
    float current_power[8];
    float current_power_calc = 0;

    float prev_power[8] = {0,0,0,0,0,0,0,0};
    int perturb_direction[8] = {1, 1, 1, 1, 1, 1, 1, 1}; // Start by increasing voltage

    int delay_per_measurement = measurement_delay_mppt/measurements_per_step_mppt;

    for (int ID = 0; ID < 8; ++ID)
    {
        // Vset ---------------------------------------------------
        vset[ID] = voltage_starting_mppt;
        setVoltage_V(vset[ID], ID);
    }

    delay(measurement_delay_mppt);

    int start_millis = millis();
    Serial.print("measurement_time (min): ");
    Serial.println(measurement_time_mins_mppt);
    while ((millis() - start_millis) / (1000.0*60.0) < measurement_time_mins_mppt)
    {
        for (int ID = 0; ID < 8; ++ID)
        {
            setVoltage_V(vset[ID], ID);
            load_voltageArr[ID] = 0.0;
            current_mA_flipped_arr[ID] = 0.0;
            current_power[ID] = 0.0;
        }

        delay(delay_per_measurement);

        for (int meas = 0; meas < measurements_per_step_mppt; meas++)
        {
            for (int ID = 0; ID < 8; ++ID)
            {
                // temp_voltage = get_voltage_V(ID);
                // temp_flipped_A = get_current_flipped_mA(ID);
                // // Measure current power at Vset[ID]
                // current_power[ID] += temp_voltage * temp_flipped_A;
                // load_voltageArr[ID] += temp_voltage;
                // current_mA_flipped_arr[ID] += get_current_flipped_mA(ID);

                load_voltage = get_voltage_V(ID);
                current_mA_Flipped = get_current_flipped_mA(ID);

                current_power[ID] += load_voltage * current_mA_Flipped;
                load_voltageArr[ID] += load_voltage;
                current_mA_flipped_arr[ID] += current_mA_Flipped;
            }
            delay(delay_per_measurement);
        }

        for (int ID = 0; ID < 8; ++ID)
        {
            current_power[ID] /= measurements_per_step_mppt;
            load_voltageArr[ID] /= measurements_per_step_mppt;
            current_mA_flipped_arr[ID] /= measurements_per_step_mppt;

            current_power_calc = load_voltageArr[ID] * current_mA_flipped_arr[ID];

            // moving average calculation
            float smoothed_power = (
                prev_power[ID] *(moving_average_n - 1) + current_power_calc)
                / moving_average_n;

            if (smoothed_power > prev_power[ID])
            {
                // Power increased, continue in the same direction
                vset[ID] += perturb_direction[ID] * voltage_step_size_mppt;
            }
            else
            {
                // Power decreased, reverse direction
                perturb_direction[ID] *= -1;
                vset[ID] += perturb_direction[ID] * voltage_step_size_mppt;
            }

            prev_power[ID] = smoothed_power;
        }
        for (int ID = 0; ID < 8; ++ID)
        {
            Serial.print(vset[ID], 3);
            Serial.print(", ");
        }
        Serial.print("1");
        Serial.println();

        Serial.print((millis() - start_millis) / 1000.0, 4);
        Serial.print(", ");
        for (int ID = 0; ID < 8; ++ID)
        {
            Serial.print(load_voltageArr[ID], 2);
            Serial.print(", ");
            Serial.print(current_mA_flipped_arr[ID], 2);
            Serial.print(", ");
        }

        for (int ID = 0; ID < 8; ++ID)
        {
            // Serial.print((prev_power[ID]/1000) / (0.1 * area_of_collector_mppt*100, 4), 5);
            // Serial.print(prev_power[ID], 5);
            Serial.print((prev_power[ID] / 1000) / (0.1 * 0.128)*100, 4);

            Serial.print(", ");
        }
        Serial.print(uniqueID);

        Serial.println("");
    }

    mppt_done = true;
    led(false);
}

// --------------------------------------------------------------------------------------

// performs forward or backward JV scan of solar cell
void scan(ScanDirection dir)
{
    led(true);

    // convert voltage_range_scan to mV, measurement_rate_scan = mV/s
    int s = (voltage_range_scan * 1000) / measurement_rate_scan;
    int steps = (voltage_range_scan * 1000) / (voltage_step_size_scan * 1000);
    // Serial.print(s); Serial.print(" "); Serial.println (steps);

    // Delay time for one measurement
    int same_step_measurement_delay = 10;

    // Calculate delay time to reach proper scan rate
    // int floored_measurements = static_cast<int>(flooredValue);
    float measurements = floor(voltage_range_scan / voltage_step_size_scan);
    float scan_rate = measurement_rate_scan/1000.0;
    float total_seconds = voltage_range_scan / scan_rate;
    float ms_per_measurement = 1000.0 * total_seconds / measurements;
    int delay_time_ms = max(0, (ms_per_measurement/measurements_per_step_scan - measurement_time));

    float direction = 1.0;

    Serial.print("Started scan with delay time: ");
    Serial.println(delay_time_ms);

    uint32_t timestart = millis();

    if (dir == SCAN_BACKWARD)
    {
        voltage_val = voltage_range_scan;
        direction = -1.0;
    }
    else if (dir == SCAN_FORWARD)
    {
        voltage_val = 0;
    }

    for (int ID = 0; ID < 8; ++ID)
    {
        setVoltage_V(voltage_val, ID);
    }

    delay(delay_time_ms);
    unsigned long start_millis = millis();

    while (voltage_range_scan >= voltage_val && voltage_val >= 0)
    {
        // Serial.print(millis()); Serial.print(" "); Serial.println(volt_Step_Count); // used to measure offset
        if (volt_step_count < measurements_per_step_scan)
        {
            for (int ID = 7; ID >= 0; --ID)
            {
                avg_volt[ID] += get_voltage_V(ID);
                avg_curr[ID] += get_current_flipped_mA(ID);
            }
            volt_step_count++;
            delay(delay_time_ms); // to set the scan rate
        }
        else
        {
            unsigned long curr_millis = millis() - start_millis;

            Serial.print(curr_millis / 1000.0, 4);
            Serial.print(",");
            Serial.print(voltage_val);
            Serial.print(",");
            for (int ID = 0; ID < 8; ++ID)
            {
                Serial.print(avg_volt[ID] / volt_step_count, 4);
                Serial.print(",");
                Serial.print(avg_curr[ID] / volt_step_count, 4);
                Serial.print(",");
            }
            Serial.print(uniqueID);
            Serial.println("");

            // reset all values in array to 0
            memset(avg_volt, 0.0, sizeof(avg_volt));
            memset(avg_curr, 0.0, sizeof(avg_curr));
            volt_step_count = 0;

            // set new voltage
            voltage_val += direction*voltage_step_size_scan;

            for (int ID = 0; ID < 8; ID++)
            {
                setVoltage_V(voltage_val, ID);
            }


        }

    }

    Serial.print("mV/s: ");
    float total_time_s = (millis() - timestart)/1000.0;
    float mv_s = 1000.0*voltage_range_scan / total_time_s;
    Serial.println(mv_s);
    scan_done = true;
    led(false);
}

void setConstantVoltage()
{
    for (int ID = 0; ID < 8; ID++)
    {
        setVoltage_V(constant_voltage, ID);
    }

    unsigned long start_millis = millis();
    while (true)
    {
        if (volt_step_count >= measurements_per_step_scan)
        {
            delay(400);
            unsigned long curr_millis = millis() - start_millis;

            Serial.print(curr_millis / 1000.0, 4);
            Serial.print(",");
            Serial.print(constant_voltage);
            Serial.print(",");
            for (int ID = 0; ID < 8; ++ID)
            {
                Serial.print(avg_volt[ID] / volt_step_count, 4);
                Serial.print(",");
                Serial.print(avg_curr[ID] / volt_step_count, 4);
                Serial.print(",");
            }
            Serial.print(1);
            Serial.println("");

            // reset all values in array to 0
            memset(avg_volt, 0.0, sizeof(avg_volt));
            memset(avg_curr, 0.0, sizeof(avg_curr));
            volt_step_count = 0;

            for (int ID = 0; ID < 8; ID++)
            {
                setVoltage_V(constant_voltage, ID);
            }

            // Serial.println("");
        }
        else
        {
            for (int ID = 0; ID < 8; ++ID)
            {
                avg_volt[ID] += get_voltage_V(ID);
                avg_curr[ID] += get_current_flipped_mA(ID);
            }
            volt_step_count++;
        }
    }
}

