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


// NOT yet working!!
void Sr04::sr04GetDistance(int *buf, unsigned long timeout) {
  // Send trigger on one sensor
  int _default = 2 *round( MAX_DISTANCE_METER/ SPEED_OF_SOUND_M_MSEC) *1000;
  int done = 0;

  int distances[SENSOR_COUNT];
  for (int s=0; s<SENSOR_COUNT; s++){
    buf[s] = _default;
  }
  
  _sr04SendTrigger(_sensors[0][TRIGGER]);
  unsigned long start = micros();
  while(start + timeout > micros()  && done <= 5){
      
    for(int s=0; s < SENSOR_COUNT; s++){
      if (digitalRead(_sensors[s][ECHO]) == HIGH && buf[s] == _default){
        buf[s] = round((micros() - start)*0.0171);
        done +=1;
      }
    }
    
  }
  delay(_sleep);

  
}



int Sr04::sr04GetDistance(int sensor, unsigned long timeout) {
  _sr04SendTrigger(_sensors[sensor][TRIGGER]);
  int pulseDuration = pulseIn(_sensors[sensor][ECHO], HIGH, timeout);
  delay(_sleep);
  if (pulseDuration==0){
    pulseDuration = 2 *round( MAX_DISTANCE_METER/ SPEED_OF_SOUND_M_MSEC) *1000;
  }
  return round(pulseDuration * 0.0171);

}
