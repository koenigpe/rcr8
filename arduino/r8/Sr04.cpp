/*
  Sr04.cpp
  Created by Peter K.
  Released into the public domain.
*/
#include "Arduino.h"
#include "Sr04.h"


Sr04::Sr04(int sensors[SENSOR_COUNT][2])
{
  for(int i=0; i <SENSOR_COUNT; i++){
    _sensors[i][TRIGGER]=sensors[i][TRIGGER];
    _sensors[i][ECHO]=sensors[i][ECHO];
  }

}

//  SR04 pinMode initialization
void Sr04::initPins() {
    for (int i=0; i< SENSOR_COUNT; i++){ 
    pinMode(_sensors[i][TRIGGER], OUTPUT); 
    pinMode(_sensors[i][ECHO], INPUT);
   }
}

int Sr04::durationToFrequency(int duration) {
  if (duration == 0){
    return 10000;
  }else {
    return map(duration, 1, 100, 50, 1000);
  }
}


void Sr04::_sr04SendTrigger(int pin){
  digitalWrite(pin, LOW);
  delayMicroseconds(5);
  digitalWrite(pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(pin, LOW);  
}


// ToDo: Test
void Sr04::sr04GetDistance(int *buf, unsigned long timeout) {

  int sensors_measured = 0;
  int _default = timeout *0.034/2;

  boolean is_high[SENSOR_COUNT];

  SENSOR_LOOP(
    buf[sensor] = _default;
    is_high[sensor] = false;
  )
  
  _sr04SendTrigger(_sensors[0][TRIGGER]);
  
  unsigned long timeout_start = micros();
  unsigned long start_measurement;

  while( !(IS_TIMEOUT) && sensors_measured < SENSOR_COUNT ){
     // Catch high 
     SENSOR_LOOP(
      if (!is_high[sensor] && digitalRead(_sensors[sensor][ECHO]) ){
        start_measurement=micros();
        is_high[sensor]=true;
      }
      // Catch low
      if (is_high[sensor] && buf[sensor] == _default && !digitalRead(_sensors[sensor][ECHO])){
        buf[sensor] = (micros() - start_measurement)*0.034/2;
        sensors_measured++; 
      }
     )       
  }

  delay(_sleep);

}



int Sr04::sr04GetDistance(int sensor, unsigned long timeout) {
  _sr04SendTrigger(_sensors[sensor][TRIGGER]);
  int pulseDuration = pulseIn(_sensors[sensor][ECHO], HIGH, timeout);
  delay(_sleep);
  if (pulseDuration==0){
    pulseDuration = timeout;
  }
  return round(pulseDuration *0.034/2);

}
