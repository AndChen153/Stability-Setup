// measurement.cpp
#include "../include/measurement.h"
#include "../include/sensor.h"
#include "../include/serial_com.h"
#include "../include/helper.h"

// Extern variables from main
extern float vset[8];
extern volatile bool mppt_done;
extern float mppt_step_size_V;
extern int mppt_measurements_per_step;
extern int mppt_delay;
extern int mppt_measurement_interval;
extern unsigned long mppt_time_mins;

extern volatile bool scan_done;
extern float avg_volt[8];
extern float avg_curr[8];
extern int volt_step_count;
extern float voltage_val;

extern float scan_range;
extern float scan_step_size;
extern int scan_read_count;
extern int scan_rate;
extern int light_status;

extern volatile bool constant_voltage_done;
extern float constant_voltage;

extern float load_voltage;
extern float current_mA_Flipped;

extern uint32_t uniqueID;

const float measurement_time = 21;
volatile uint32_t measurement_millis;

bool plausible(float V, float I) {
    return  (V >= -0.05 && V <=  2.5) &&       // perovskite Voc window
            (I >= -0.2  && I <= 25.0);         // –0.2 mA..25 mA for your shunt
}

void perturbAndObserveClassic()
{
    led(true);
    light_control(1);
    // Serial.println(F("")
    // TODO: use longer moving average or more complex filter
    float moving_average_n = 5;
    int count;
    float temp_voltage = 0.0;
    float temp_flipped_A = 0.0;
    float load_voltageArr[8];
    int measurements[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    float current_mA_flipped_arr[8];
    float current_power[8];
    float current_power_calc = 0;

    float prev_power[8] = {0,0,0,0,0,0,0,0};
    int perturb_direction[8] = {1, 1, 1, 1, 1, 1, 1, 1}; // Start by increasing voltage
    int measurement_time = 15;
    int delay_per_measurement = mppt_measurement_interval/mppt_measurements_per_step - measurement_time;
    if (delay_per_measurement < 0) {
        delay_per_measurement = 0;
    }
    Serial.print(F("Delay: "));
    Serial.println(delay_per_measurement);

    for (int ID = 0; ID < 8; ++ID) setVoltage_V(vset[ID], ID);

    delay(delay_per_measurement);
    int start_millis = millis();
    Serial.print(F("measurement_time (min): "));
    Serial.println(mppt_time_mins);
    while ((millis() - start_millis) / (1000.0*60.0) < mppt_time_mins)
    {
        for (int ID = 0; ID < 8; ++ID)
        {
            setVoltage_V(vset[ID], ID);
            load_voltageArr[ID] = 0.0;
            current_mA_flipped_arr[ID] = 0.0;
            current_power[ID] = 0.0;
        }

        delay(mppt_delay);
        measurement_millis = millis();

        int total_measurements = 0;
        memset(measurements, 0, sizeof(measurements));
        while (total_measurements < mppt_measurements_per_step && (millis() - measurement_millis) < mppt_measurement_interval) {
            total_measurements++;
            for (int ID = 0; ID < 8; ++ID)
            {
                load_voltage = get_voltage_V(ID);
                current_mA_Flipped = get_current_flipped_mA(ID);
                if (!plausible(load_voltage, current_mA_Flipped)) continue;

                measurements[ID]++;
                current_power[ID] += load_voltage * current_mA_Flipped;
                load_voltageArr[ID] += load_voltage;
                current_mA_flipped_arr[ID] += current_mA_Flipped;
            }
            delay(delay_per_measurement);
        }

        for (int ID = 0; ID < 8; ++ID)
        {
            if (measurements[ID] > 0) {
                current_power[ID] /= measurements[ID];
                load_voltageArr[ID] /= measurements[ID];
                current_mA_flipped_arr[ID] /= measurements[ID];

                current_power_calc = load_voltageArr[ID] * current_mA_flipped_arr[ID];
            }


            // moving average calculation
            float smoothed_power = current_power_calc;
            // (
            //     prev_power[ID] *(moving_average_n - 1) + current_power_calc)
            //     / moving_average_n;

            if (smoothed_power > prev_power[ID])
            {
                // Power increased, continue in the same direction
                vset[ID] += perturb_direction[ID] * mppt_step_size_V;
            }
            else
            {
                // Power decreased, reverse direction
                perturb_direction[ID] *= -1;
                vset[ID] += perturb_direction[ID] * mppt_step_size_V;
            }

            prev_power[ID] = smoothed_power;
        }

        Serial.print((millis() - start_millis) / 1000.0, 4);
        Serial.print(F(", "));
        for (int ID = 0; ID < 8; ++ID)
        {
            Serial.print(load_voltageArr[ID], 10);
            Serial.print(F(", "));
            Serial.print(current_mA_flipped_arr[ID], 5);
            Serial.print(F(", "));
        }

        Serial.print(uniqueID);

        Serial.println(F(""));
    }

    mppt_done = true;
    led(false);
}

// --------------------------------------------------------------------------------------

// performs forward or backward JV scan of solar cell
// TODO: recalculate scan timing every step
void scan(ScanDirection dir)
{
    led(true);

    // convert scan_range to mV, scan_rate = mV/s
    int seconds = (scan_range * 1000) / scan_rate; // 1.2*1000/50 = 24 seconds
    int steps = (scan_range * 1000) / (scan_step_size * 1000); //= 40 steps
    // Serial.print(F(s)); Serial.print(F(s)); Serial.println (steps);

    // Calculate delay time to reach proper scan rate
    // int floored_measurements = static_cast<int>(flooredValue);
    float ms_per_measurement = 1000.0 * seconds / steps;
    int delay_time_ms = ms_per_measurement/scan_read_count - measurement_time;
    if (delay_time_ms < 0) {
        delay_time_ms = 0;
    }

    float direction = 1.0;

    Serial.print(F("Started scan with delay time: "));
    Serial.println(delay_time_ms);

    uint32_t timestart = millis();

    if (dir == SCAN_BACKWARD)
    {
        voltage_val = scan_range;
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

    while (scan_range >= voltage_val && voltage_val >= 0)
    {
        // Serial.print(F(millis()); Serial.print(F(" ")); Serial.print(F(" ")); // used to measure offset
        if (volt_step_count < scan_read_count)
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
            Serial.print(F(","));
            Serial.print(voltage_val);
            Serial.print(F(","));
            for (int ID = 0; ID < 8; ++ID)
            {
                Serial.print(avg_volt[ID] / volt_step_count, 10);
                Serial.print(F(","));
                Serial.print(avg_curr[ID] / volt_step_count, 5);
                Serial.print(F(","));
            }
            Serial.print(uniqueID);
            Serial.println(F(""));

            // reset all values in array to 0
            memset(avg_volt, 0.0, sizeof(avg_volt));
            memset(avg_curr, 0.0, sizeof(avg_curr));
            volt_step_count = 0;

            // set new voltage
            voltage_val += direction*scan_step_size;

            for (int ID = 0; ID < 8; ID++)
            {
                setVoltage_V(voltage_val, ID);
            }


        }

    }

    Serial.print(F("mV/s: "));
    float total_time_s = (millis() - timestart)/1000.0;
    float mv_s = 1000.0*scan_range / total_time_s;
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
        if (volt_step_count >= scan_read_count)
        {
            delay(400);
            unsigned long curr_millis = millis() - start_millis;

            Serial.print(curr_millis / 1000.0, 4);
            Serial.print(F(","));
            Serial.print(constant_voltage);
            Serial.print(F(","));
            for (int ID = 0; ID < 8; ++ID)
            {
                Serial.print(avg_volt[ID] / volt_step_count, 4);
                Serial.print(F(","));
                Serial.print(avg_curr[ID] / volt_step_count, 4);
                Serial.print(F(","));
            }
            Serial.print(F("1"));
            Serial.println(F(""));

            // reset all values in array to 0
            memset(avg_volt, 0.0, sizeof(avg_volt));
            memset(avg_curr, 0.0, sizeof(avg_curr));
            volt_step_count = 0;

            for (int ID = 0; ID < 8; ID++)
            {
                setVoltage_V(constant_voltage, ID);
            }

            // Serial.println(F(""));
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

