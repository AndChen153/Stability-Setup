// serial_comm.h
#ifndef SERIAL_COMM_H
#define SERIAL_COMM_H

#include <Arduino.h>

static const byte num_chars = 32;

enum serialCommResult {
    NONE,
    START,
};

static const String Modes[3] = {"scan", "PnO", "constantVoltage"};

serialCommResult recvWithLineTermination();
bool checkForStopMessage();
bool check_valid_mode();
void clearSerialBuffer();
void show_parsed_data();

#endif
