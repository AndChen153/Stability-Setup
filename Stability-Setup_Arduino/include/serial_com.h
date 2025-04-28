// serial_comm.h
#ifndef SERIAL_COMM_H
#define SERIAL_COMM_H
#include <string.h>
#include <Arduino.h>
#define NUM_CHARS 30
#define MAX_MODE_LEN 5


// --- Declare global variables used across files using extern ---
// These variables must be DEFINED in ONE .cpp or .ino file

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


enum serialCommResult {
    NONE,
    START,
};

serialCommResult recvWithLineTermination();
void showParsedData();

#endif
