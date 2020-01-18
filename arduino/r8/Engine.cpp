

/*
  Engine.cpp
  Created by Peter K.
  Released into the public domain.
*/

#include "Arduino.h"
#include "Engine.h"

Engine::Engine(int engines[ENGINE_COUNT][3])
{
  for(int i=0; i <ENGINE_COUNT; i++){
    _engines[i][PIN1]=engines[i][PIN1];
    _engines[i][PIN2]=engines[i][PIN2];
    _engines[i][PIN_PWM]=engines[i][PIN_PWM];
  }

}

void Engine::initPins() {
  for (int i=0; i< ENGINE_COUNT; i++){ 
    pinMode(_engines[i][PIN1], OUTPUT); 
    pinMode(_engines[i][PIN2], OUTPUT);
    pinMode(_engines[i][PIN_PWM], OUTPUT);
    analogWrite(_engines[i][PIN_PWM], 0);
   }
}


void Engine::testSteering(){
  // Steering Test
  
  steer(TURN_LEFT);  
  accellerate(V_MAX);delay(500);
  accellerate(0);delay(500);
  accellerate(0);delay(500);
    
  steer(TURN_RIGHT);  
  accellerate(-V_MAX);delay(500);
  accellerate(0);delay(500);
  accellerate(0);delay(500);
    


}

void Engine::testAccelleration(){
    
  accellerate(V_MAX);delay(500);
  accellerate(0);delay(500);
  accellerate(0);delay(500);
  accellerate(0);delay(500);
  accellerate(-V_MAX);delay(500);
  accellerate(0);delay(500);
  accellerate(0);delay(500);
  accellerate(0);delay(250);
}


void Engine::_setOpposite(int activePin, int inactivePin){
  digitalWrite(activePin, HIGH); 
  digitalWrite(inactivePin, LOW); 
}

void Engine::accellerate(int pwmSpeed){

  if (pwmSpeed <0){
    _setOpposite(_engines[ACCELLERATION][PIN1], _engines[ACCELLERATION][PIN2]);
  } else {
    _setOpposite(_engines[ACCELLERATION][PIN2], _engines[ACCELLERATION][PIN1]);
  }

  int pwmLimited=pwmSpeed;
  // Limit accelleration
  if (pwmSpeed > V_MAX) {pwmLimited=V_MAX;}
  if (pwmSpeed < -V_MAX) {pwmLimited=-V_MAX;}
  
  if( _currentAccelleration - pwmLimited  > MAX_D_V) { pwmLimited=_currentAccelleration - MAX_D_V;}
  if( _currentAccelleration - pwmLimited  < -MAX_D_V) { pwmLimited=_currentAccelleration + MAX_D_V;}
  _currentAccelleration=pwmLimited;
  analogWrite(_engines[ACCELLERATION][PIN_PWM], abs(pwmLimited));
}

void Engine::steer(int steerDirection){
  switch(steerDirection){
    case (TURN_RIGHT):
      _setOpposite(_engines[STEER][PIN1], _engines[STEER][PIN2]);
      analogWrite(_engines[STEER][PIN_PWM], 200);
      break;
    case (TURN_LEFT):
      _setOpposite(_engines[STEER][PIN2], _engines[STEER][PIN1]);
      analogWrite(_engines[STEER][PIN_PWM], 200);  
      break;
    default:
      analogWrite(_engines[STEER][PIN_PWM], 0);
      digitalWrite(_engines[STEER][PIN1], LOW);
      digitalWrite(_engines[STEER][PIN2], LOW);
      break;
  }
}
