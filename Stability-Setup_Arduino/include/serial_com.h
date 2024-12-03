// serial_comm.h
#ifndef SERIAL_COMM_H
#define SERIAL_COMM_H

#include <Arduino.h>

static const byte num_chars = 32;

void recvWithStartEndMarkers();
void parse_data();
void show_parsed_data();

#endif
