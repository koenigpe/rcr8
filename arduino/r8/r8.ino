/*
  Check all components of the R8

  Components:
    Led
    Motor 1
    Motor 2
    SR_04 1
    SR_04 2
    SR_04 3
    
  by Peter König

*/

#include <SoftwareSerial.h>
#include "BlinkLeds.h"
#include "Sr04.h"
#include "Engine.h"


// SETUP LEDs
#define FRONT_RIGHT  0
#define RIGHT  1
#define BACK 2
#define LEFT 3
#define FRONT_LEFT 4
int led_pins[5] = {14, 15, 16, 17, 18};
BlinkLeds leds(led_pins);

// SETUP SR04
int sr04_pins[5][2] = {
  { 7, 6},
  { 7, 2},
  { 7, 4},
  { 7, 3},
  { 7, 5}                       
};
Sr04 sr04(sr04_pins);
int distances[5];

// SETUP ENGINE
int engine_pins[2][3] = {
  //Motor1 (Steer)
    {0, 19 , 11  },
  //Motor2 (Accellerate)
    { 12, 13, 10  }
};
Engine engine(engine_pins);

// SETUP BLUETOOTH
#define maxMessage 32
#define timeout 50
byte message[maxMessage];
int btTxd = 8;
int btRxd = 9;
SoftwareSerial hc06(btTxd, btRxd);

byte readWithTimeout(){
  long startTime = millis();
  while(startTime+timeout > millis() ){
    if (hc06.available() > 0 ) {
      return hc06.read();
    }
  }
}

void sendSensorData(){
  for (int s =0; s<5;s++){
    hc06.write(distances[s]);  
  }
}

void processRcMessage(){
  byte cmd = readWithTimeout();
  if(char(cmd) =='d') {sendSensorData();}
  if(char(cmd) =='a') {processAccelleration();}
  if(char(cmd) =='s') {processSteering();}
}

void processMessage(){
  
  int i=0;
  byte c = hc06.read();

  if (char(c)==':'){
    processRcMessage();
  }

}

int targetSpeed;
void processAccelleration(){
  targetSpeed = readWithTimeout()-1;
}

int targetSteer;
void processSteering(){
  targetSteer = readWithTimeout()-1;
}





void sensorUpdate(){


 // sr04.sr04GetDistance(distances);
  for (int s=0; s<5; s++){
    distances[s] = sr04.sr04GetDistance(s);
    //sr04.sr04GetDistance(s)
    leds.setFrequency(s, sr04.durationToFrequency(distances[s]));
  }  

  leds.turnOnOff();
}


// the setup function runs once when you press reset or power the board
void setup() {
  engine.initPins();
  leds.initPins();
  sr04.initPins();
  hc06.begin(9600);



 // engine.testAccelleration();
 // engine.testSteering();
}

boolean stuck = false;
void checkIfStuck(){

  if (distances[FRONT_LEFT] <10 || distances[FRONT_RIGHT] < 10 || distances[BACK] <10 || stuck){
    targetSpeed = 0;
    targetSteer = GO_AHEAD;
    stuck=true;
    engine.steer(0);
    engine.accellerate(0);
    leds.emergency();
  }
}


// the loop function runs over and over again forever
void loop() {
  sensorUpdate();
  //checkIfStuck();


  if (hc06.available() > 0 ) {
      processMessage();
      engine.steer(targetSteer);
      engine.accellerate(targetSpeed*V_MAX);
   }

 
 //stateToSerial();
/*
 engine.steer(targetSteer);
 engine.accellerate(targetSpeed);
*/


}
