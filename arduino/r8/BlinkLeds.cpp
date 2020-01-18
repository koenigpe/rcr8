/*
  BlinkLeds.cpp
  Created by Peter K.
  Released into the public domain.
*/

#include "Arduino.h"
#include "BlinkLeds.h"

BlinkLeds::BlinkLeds(int pins[LED_COUNT])
{
  for(int i=0; i <LED_COUNT; i++){
     _pins[i] = pins[i];
  }

}

void BlinkLeds::emergency(){
  for (int i = 0; i < LED_COUNT; i++ ) {
    digitalWrite(_pins[i], HIGH);
  }
  delay(50);
  for (int i = 0; i < LED_COUNT; i++ ) {
    digitalWrite(_pins[i], LOW);
  }
}

void BlinkLeds::turnOnOff() {
  for (int i = 0; i < LED_COUNT; i++ ) {
    // turn on 
    if (millis() > _ledActivationMillis[i] + _frequencyOn[i]){
      digitalWrite(_pins[i], HIGH);
      _ledActivationMillis[i] = millis();
    }

    // turn off
    if (digitalRead(_pins[i]) && millis() > _ledActivationMillis[i] + _durationOn){
      digitalWrite(_pins[i], LOW);

    }
  }
}


void BlinkLeds::initPins() {
  for (int i=0; i< LED_COUNT; i++){ 
    pinMode(_pins[i], OUTPUT); 
    digitalWrite(_pins[i], HIGH);

   }
   
   // Startup countdown
   delay(1000);
   for (int i=0; i< LED_COUNT; i++){ 
        delay(500);
        digitalWrite(_pins[i], LOW);
   }
   delay(1000);

}

void BlinkLeds::setFrequency(int pin, int frequencyOn) {
  _frequencyOn[pin] = frequencyOn;
}
