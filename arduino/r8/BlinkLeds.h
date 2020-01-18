/*
  BlinkLeds.h
  Created by Peter K.
  Released into the public domain.
*/
#ifndef R8led_h
#define flashing Morse code.

#include "Arduino.h"

#define LED_COUNT 5

class BlinkLeds
{
  public:
    BlinkLeds(int led[LED_COUNT]);
    void turnOnOff();
    void initPins();
    void setFrequency(int pin, int frequency);
    void emergency();
    
	
  private:
    int _pins[LED_COUNT];
    int _frequencyOn[LED_COUNT] = {500,500,500};
    long _ledActivationMillis[LED_COUNT];
    int _durationOn = 50;

};

#endif
