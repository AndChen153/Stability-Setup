// serial_comm.h
#ifndef SERIAL_COMM_H
#define SERIAL_COMM_H

#include <Arduino.h>

static const byte num_chars = 64;

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
