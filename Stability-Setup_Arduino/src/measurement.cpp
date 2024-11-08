// measurement.cpp
#include "../include/measurement.h"
#include "../include/sensor.h"
#include "../include/serial_com.h"
#include "../include/helper.h"
#include <Arduino.h>

// Extern variables from main
extern float Vset[8];
extern boolean perturb_And_ObserveDone;
extern float voltage_starting_pno;
extern float voltage_step_size_pno;
extern int measurement_delay_pno;
extern int measurements_per_step_pno;
extern unsigned long measurement_time_mins;

extern boolean scan_done;
extern float avgVolt[8];
extern float avgCurr[8];
extern int volt_Step_Count;
extern float voltage_val;

extern float voltage_Range_Scan;
extern float voltage_Step_Size_Scan;
extern int measurements_Per_Step_Scan;
extern int measurement_Rate_Scan;
extern int light_Status;

extern boolean constant_voltage_done;
extern float constant_voltage;

extern float load_voltage;
extern float current_mA_Flipped;

void perturb_and_observe()
{
    led(true);
    light_control(1);

    float VsetUp;
    float VsetDown;
    float time;

    int count;

    float avgPowerCalced[8];
    // float avgPowerCalcedUp;
    // float avgPowerCalcedDown;
    float avgPowerCalcedUp[8];
    float avgPowerCalcedDown[8];
    float load_voltageArr[8];
    float current_mA_FlippedArr[8];
    float PCE[8];
    // measurements_per_step_pno++; // average not working correctly

    for (int ID = 0; ID < 8; ++ID)
    {
        // Vset ---------------------------------------------------
        setVoltage(&allDAC[ID], Vset[ID], ID);
    }
    delay(measurement_delay_pno);

    int currentMillis = 0;
    int pm = millis();
    int startMillis = millis();
    Serial.print("measurement_time (min): ");
    Serial.println(measurement_time_mins);
    while ((millis() - startMillis) / (1000.0*60.0) < measurement_time_mins)
    {
        for (int i = 0; i < 8; ++i)
        {
            avgPowerCalced[i] = 0.0;
            avgPowerCalcedUp[i] = 0.0;
            avgPowerCalcedDown[i] = 0.0;
            load_voltageArr[i] = 0.0;
            current_mA_FlippedArr[i] = 0.0;
        }

        // Vset ---------------------------------------------------
        for (int ID = 0; ID < 8; ++ID)
        {
            setVoltage(&allDAC[ID], Vset[ID], ID);
            delay(measurement_delay_pno);

            for (int i = 0; i < measurements_per_step_pno; ++i)
            {
                getINA129(&allINA219[ID], ID);
                avgPowerCalced[ID] += load_voltage * current_mA_Flipped;
                load_voltageArr[ID] += load_voltage;
                current_mA_FlippedArr[ID] += current_mA_Flipped;
            }
        }

        // Vset + deltaV ------------------------------------------
        for (int ID = 0; ID < 8; ++ID)
        {
            VsetUp = Vset[ID] + voltage_step_size_pno;
            setVoltage(&allDAC[ID], VsetUp, ID);
            delay(measurement_delay_pno);

            for (int i = 0; i < measurements_per_step_pno; ++i)
            {
                getINA129(&allINA219[ID], ID);
                avgPowerCalcedUp[ID] += load_voltage * current_mA_Flipped;
            }
            // zero();
        }

        // Vset - deltaV ------------------------------------------
        for (int ID = 0; ID < 8; ++ID)
        {

            VsetDown = Vset[ID] - voltage_step_size_pno;
            setVoltage(&allDAC[ID], VsetDown, ID);
            delay(measurement_delay_pno);

            for (int i = 0; i < measurements_per_step_pno; ++i)
            {
                getINA129(&allINA219[ID], ID);
                avgPowerCalcedDown[ID] += load_voltage * current_mA_Flipped;
            }
        }
        // Measurements -----------------------------------------
        for (int ID = 0; ID < 8; ++ID)
        {

            // zero();
            avgPowerCalced[ID] = avgPowerCalced[ID] / measurements_per_step_pno;
            avgPowerCalcedUp[ID] = avgPowerCalcedUp[ID] / measurements_per_step_pno;
            avgPowerCalcedDown[ID] = avgPowerCalcedDown[ID] / measurements_per_step_pno;
            load_voltageArr[ID] = load_voltageArr[ID] / measurements_per_step_pno;
            current_mA_FlippedArr[ID] = current_mA_FlippedArr[ID] / measurements_per_step_pno;

            if (avgPowerCalcedUp[ID] > avgPowerCalcedDown[ID] &&
                avgPowerCalcedUp[ID] > avgPowerCalced[ID])
            {
                Vset[ID] += voltage_step_size_pno;
            }
            else if (avgPowerCalcedDown[ID] > avgPowerCalcedUp[ID] &&
                     avgPowerCalcedDown[ID] > avgPowerCalced[ID])
            {
                Vset[ID] -= voltage_step_size_pno;
            }

            PCE[ID] = (avgPowerCalced[ID] / 1000) / (0.1 * 0.128);
        }
        currentMillis = currentMillis + millis() - pm;
        pm = millis();
        Serial.print((millis() - startMillis) / 1000.0, 4);
        Serial.print(", ");
        for (int ID = 0; ID < 8; ++ID)
        {
            Serial.print(load_voltageArr[ID], 2);
            Serial.print(", ");
            Serial.print(current_mA_FlippedArr[ID], 2);
            Serial.print(", ");
        }

        for (int ID = 0; ID < 8; ++ID)
        {
            Serial.print((PCE[ID] * 100), 4);
            Serial.print(", ");
        }
        Serial.print(0);

        Serial.println("");
    }
    // while ((millis() - startMillis) / 1000.0 < measurement_time_mins)
    // {
    //     // measurements_per_step_pno

    //     for (int ID = 0; ID < 8; ++ID)
    //     {
    //         // Vset + deltaV ------------------------------------------
    //         VsetUp = Vset[ID] + voltage_step_size_pno;
    //         setVoltage(&allDAC[ID], VsetUp, ID);
    //         delay(measurement_delay_pno);

    //         for (int i = 0; i < measurements_per_step_pno; ++i)
    //         {
    //             getINA129(&allINA219[ID], ID);
    //             avgPowerCalcedUp += load_voltage * current_mA_Flipped;
    //         }

    //         // Vset ---------------------------------------------------
    //         setVoltage(&allDAC[ID], Vset[ID], ID);
    //         delay(measurement_delay_pno);

    //         for (int i = 0; i < measurements_per_step_pno; ++i)
    //         {
    //             getINA129(&allINA219[ID], ID);
    //             avgPowerCalced[ID] += load_voltage * current_mA_Flipped;
    //             load_voltageArr[ID] += load_voltage;
    //             current_mA_FlippedArr[ID] += current_mA_Flipped;
    //         }

    //         // Vset - deltaV ------------------------------------------
    //         VsetDown = Vset[ID] - voltage_step_size_pno;
    //         setVoltage(&allDAC[ID], VsetDown, ID);
    //         delay(measurement_delay_pno);

    //         for (int i = 0; i < measurements_per_step_pno; ++i)
    //         {
    //             getINA129(&allINA219[ID], ID);
    //             avgPowerCalcedDown += load_voltage * current_mA_Flipped;
    //         }

    //         // zero();

    //         // zero();
    //         avgPowerCalced[ID] = avgPowerCalced[ID] / measurements_per_step_pno;
    //         avgPowerCalcedUp = avgPowerCalcedUp / measurements_per_step_pno;
    //         avgPowerCalcedDown = avgPowerCalcedDown / measurements_per_step_pno;
    //         load_voltageArr[ID] = load_voltageArr[ID] / measurements_per_step_pno;
    //         current_mA_FlippedArr[ID] = current_mA_FlippedArr[ID] / measurements_per_step_pno;

    //         if (avgPowerCalcedUp > avgPowerCalcedDown && avgPowerCalcedUp > avgPowerCalced[ID])
    //         {
    //             Vset[ID] += voltage_step_size_pno;
    //         }
    //         else if (avgPowerCalcedDown > avgPowerCalcedUp && avgPowerCalcedDown > avgPowerCalced[ID])
    //         {
    //             Vset[ID] -= voltage_step_size_pno;
    //         }

    //         PCE[ID] = (avgPowerCalced[ID] / 1000) / (0.1 * 0.128);
    //         delay(measurement_delay_pno);
    //     }

    //     currentMillis = currentMillis + millis() - pm;
    //     pm = millis();
    //     Serial.print((millis() - startMillis) / 1000.0, 4);
    //     Serial.print(", ");
    //     for (int ID = 0; ID < 8; ++ID)
    //     {
    //         Serial.print(load_voltageArr[ID], 2);
    //         Serial.print(", ");
    //         Serial.print(current_mA_FlippedArr[ID], 2);
    //         Serial.print(", ");
    //     }

    //     for (int ID = 0; ID < 8; ++ID)
    //     {
    //         Serial.print((PCE[ID] * 100), 4);
    //         Serial.print(", ");
    //     }
    //     Serial.print(0);

    //     Serial.println("");
    // }

    perturb_And_ObserveDone = true;
    led(false);
}

void perturb_and_observe_classic()
{
    led(true);
    light_control(1);
    // TODO: use longer moving average or more complex filter
    float moving_average_n = 5;
    int count;
    float load_voltageArr[8];
    float current_mA_FlippedArr[8];
    float currentPower[8];

    float prevPower[8] = {0};
    int perturbDirection[8] = {1}; // Start by increasing voltage

    for (int ID = 0; ID < 8; ++ID)
    {
        // Vset ---------------------------------------------------
        setVoltage(&allDAC[ID], Vset[ID], ID);
    }

    delay(measurement_delay_pno);

    int startMillis = millis();
    Serial.print("measurement_time (min): ");
    Serial.println(measurement_time_mins);
    while ((millis() - startMillis) / (1000.0*60.0) < measurement_time_mins)
    {
        for (int ID = 0; ID < 8; ++ID)
        {
            setVoltage(&allDAC[ID], Vset[ID], ID);
            load_voltageArr[ID] = 0.0;
            current_mA_FlippedArr[ID] = 0.0;
            currentPower[ID] = 0.0;
        }

        delay(measurement_delay_pno);

        for (int meas = 0; meas < measurements_per_step_pno; meas++)
        {
            for (int ID = 0; ID < 8; ++ID)
            {
                // Measure current power at Vset[ID]
                getINA129(&allINA219[ID], ID);
                currentPower[ID] += load_voltage * current_mA_Flipped;
                load_voltageArr[ID] += load_voltage;
                current_mA_FlippedArr[ID] += current_mA_Flipped;
            }
        }

        for (int ID = 0; ID < 8; ++ID)
        {
            currentPower[ID] /= measurements_per_step_pno;
            load_voltageArr[ID] /= measurements_per_step_pno;
            current_mA_FlippedArr[ID] /= measurements_per_step_pno;

            float smoothedPower = (prevPower[ID] * (moving_average_n - 1) + currentPower[ID]) / moving_average_n;

            if (smoothedPower > prevPower[ID])
            {
                // Power increased, continue in the same direction
                Vset[ID] += perturbDirection[ID] * voltage_step_size_pno;
            }
            else
            {
                // Power decreased, reverse direction
                perturbDirection[ID] *= -1;
                Vset[ID] += perturbDirection[ID] * voltage_step_size_pno;
            }

            prevPower[ID] = smoothedPower;
        }

        Serial.print((millis() - startMillis) / 1000.0, 4);
        Serial.print(", ");
        for (int ID = 0; ID < 8; ++ID)
        {
            Serial.print(load_voltageArr[ID], 2);
            Serial.print(", ");
            Serial.print(current_mA_FlippedArr[ID], 2);
            Serial.print(", ");
        }

        for (int ID = 0; ID < 8; ++ID)
        {
            Serial.print((prevPower[ID] / 1000) / (0.1 * 0.128)*100, 4);
            Serial.print(", ");
        }
        Serial.print(0);

        Serial.println("");
    }

    perturb_And_ObserveDone = true;
    led(false);
}

// --------------------------------------------------------------------------------------

// performs forward or backward JV scan of solar cell
void scan(String dir)
{
    led(true);

    // convert voltage_Range_Scan to mV, measurement_Rate_Scan = mV/s
    int s = (voltage_Range_Scan * 1000) / measurement_Rate_Scan;
    int steps = (voltage_Range_Scan * 1000) / (voltage_Step_Size_Scan * 1000);
    // Serial.print(s); Serial.print(" "); Serial.println (steps);

    // amount of time it takes to take measurement from all 8 ina219 on ARDUINO UNO
    // must change this on different setup
    int OFFSET = 35;

    // int delayTimeMS = (s * 1000) / steps - (OFFSET * measurements_Per_Step_Scan);
    // if (delayTimeMS < 0)
    // {
    //     delayTimeMS = 0;
    // }

    int delayTimeMS = 300;

    Serial.print("started scan with delay time: ");
    Serial.println(delayTimeMS);

    float upperLimit;
    if (dir == "backward")
    {
        voltage_val = voltage_Range_Scan;
    }
    else if (dir == "forward")
    {
        voltage_val = 0;
    }
    upperLimit = voltage_Range_Scan;

    for (int ID = 0; ID < 8; ++ID)
    {
        setVoltage(&allDAC[ID], voltage_val, ID);
    }

    delay(delayTimeMS);
    unsigned long startMillis = millis();

    while (upperLimit >= voltage_val && voltage_val >= 0)
    {
        // Serial.print(millis()); Serial.print(" "); Serial.println(volt_Step_Count); // used to measure offset
        if (volt_Step_Count >= measurements_Per_Step_Scan)
        {
            delay(delayTimeMS); // to set the scan rate
            unsigned long currMillis = millis() - startMillis;

            Serial.print(currMillis / 1000.0, 4);
            Serial.print(",");
            Serial.print(voltage_val);
            Serial.print(",");
            for (int ID = 0; ID < 8; ++ID)
            {
                Serial.print(avgVolt[ID] / volt_Step_Count, 4);
                Serial.print(",");
                Serial.print(avgCurr[ID] / volt_Step_Count, 4);
                Serial.print(",");
            }
            Serial.print(1);
            Serial.println("");

            // reset all values in array to 0
            memset(avgVolt, 0.0, sizeof(avgVolt));
            memset(avgCurr, 0.0, sizeof(avgCurr));
            volt_Step_Count = 0;

            // set new voltage
            if (dir == "backward")
            {
                voltage_val -= voltage_Step_Size_Scan;
            }
            else if (dir == "forward")
            {
                voltage_val += voltage_Step_Size_Scan;
            }

            for (int ID = 0; ID < 8; ID++)
            {
                setVoltage(&allDAC[ID], voltage_val, ID);
            }

            // Serial.println("");
        }
        else
        {
            for (int ID = 0; ID < 8; ++ID)
            {
                getINA129(&allINA219[ID], ID);
                avgVolt[ID] += load_voltage;
                avgCurr[ID] += current_mA_Flipped;
            }
            volt_Step_Count++;
        }
    }

    scan_done = true;
    led(false);
}

void set_constant_voltage()
{
    for (int ID = 0; ID < 8; ID++)
    {
        setVoltage(&allDAC[ID], constant_voltage, ID);
    }

    unsigned long startMillis = millis();
    while (true)
    {

        if (volt_Step_Count >= measurements_Per_Step_Scan)
        {
            delay(400);
            unsigned long currMillis = millis() - startMillis;

            Serial.print(currMillis / 1000.0, 4);
            Serial.print(",");
            Serial.print(constant_voltage);
            Serial.print(",");
            for (int ID = 0; ID < 8; ++ID)
            {
                Serial.print(avgVolt[ID] / volt_Step_Count, 4);
                Serial.print(",");
                Serial.print(avgCurr[ID] / volt_Step_Count, 4);
                Serial.print(",");
            }
            Serial.print(1);
            Serial.println("");

            // reset all values in array to 0
            memset(avgVolt, 0.0, sizeof(avgVolt));
            memset(avgCurr, 0.0, sizeof(avgCurr));
            volt_Step_Count = 0;

            for (int ID = 0; ID < 8; ID++)
            {
                setVoltage(&allDAC[ID], constant_voltage, ID);
            }

            // Serial.println("");
        }
        else
        {
            for (int ID = 0; ID < 8; ++ID)
            {
                getINA129(&allINA219[ID], ID);
                avgVolt[ID] += load_voltage;
                avgCurr[ID] += current_mA_Flipped;
            }
            volt_Step_Count++;
        }
    }
}