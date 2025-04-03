// serial_comm.h
#ifndef SERIAL_COMM_H
#define SERIAL_COMM_H

#include <Arduino.h>

const unsigned int num_chars = 200;
const unsigned int MAX_MODE_LEN = 32;       // Max length for "scan", "mppt", etc.

enum serialCommResult {
    NONE,
    START,
};

static const String Modes[3] = {"scan", "PnO", "constantVoltage"};

serialCommResult recvWithLineTermination();
bool checkForStopMessage();
void clearSerialBuffer();
void showParsedData();

#endif
