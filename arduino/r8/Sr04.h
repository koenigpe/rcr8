/*
  Sr04.h
  Created by Peter K.
  Released into the public domain.
*/
#ifndef Sr04_h
#define Sr04_h

#include "Arduino.h"

#define SENSOR_COUNT 5
#define TRIGGER 0
#define ECHO 1
#define SPEED_OF_SOUND_M_MSEC 0.343
#define MIN_DISTANCE_BETWEEN_MEASUREMENTS_M 8
#define MAX_DISTANCE_METER 2
#define IS_TIMEOUT micros() > timeout_start + timeout
#define SENSOR_LOOP(cmd) for (int sensor = 0; sensor < SENSOR_COUNT; sensor++){ \
    cmd \
  }

class Sr04
{
  public:
    Sr04(int sensors[SENSOR_COUNT][2]);
    int sr04GetDistance(int sensor, unsigned long timeout = 2 * round( MAX_DISTANCE_METER/ SPEED_OF_SOUND_M_MSEC)*1000);
    void sr04GetDistance(int *buf, unsigned long timeout = 2 * round( MAX_DISTANCE_METER/ SPEED_OF_SOUND_M_MSEC)*1000);
    void initPins();
    int durationToFrequency(int duration);
   
  private:
    int _sensors[SENSOR_COUNT][2];
    void _sr04SendTrigger(int pin);
    int _durationOn = 50;
    int _sleep = MIN_DISTANCE_BETWEEN_MEASUREMENTS_M / SPEED_OF_SOUND_M_MSEC;

};

#endif
