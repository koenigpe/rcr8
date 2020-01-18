/*
  Engine.h
  Created by Peter K.
  Released into the public domain.
*/
#ifndef Engine_h
#define Engine_h

#include "Arduino.h"

#define ENGINE_COUNT 2
#define PIN1 0
#define PIN2 1
#define PIN_PWM 2
#define STEER 0
#define ACCELLERATION 1
#define V_MAX 125
#define MAX_D_V 200
#define TURN_LEFT -1
#define TURN_RIGHT 1
#define GO_AHEAD 0




class Engine
{
  public:
    Engine(int engines[ENGINE_COUNT][3]);
    void initPins();
    // pwm_speed -255 (Vmax backwards) to +255 (Vmax foreward)
    void accellerate(int pwm_speed);
    void steer(int steerDirection);
    void testSteering();
    void testAccelleration();
       
    
  private:
    int _engines[ENGINE_COUNT][3];
    int _currentAccelleration=0;
    void _setOpposite(int activePin, int inactivePin);


};

#endif
