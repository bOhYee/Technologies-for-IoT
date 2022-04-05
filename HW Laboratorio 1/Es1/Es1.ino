#include <TimerOne.h>

const int LED_RED=12;
const int LED_GREEN=11;

const float HALF_P_RED=1.5;
const float HALF_P_GREEN=3.5;

int green_state=LOW;
int red_state=LOW;

void blinkGreen(){
  green_state=!green_state; //inverto lo stato
  digitalWrite(LED_GREEN,green_state);
  }
  
void setup() {
  pinMode(LED_RED,OUTPUT);
  pinMode(LED_GREEN,OUTPUT);
  Timer1.initialize(HALF_P_GREEN*1e06);
  Timer1.attachInterrupt(blinkGreen);
}

void loop() {
  red_state=!red_state;
  digitalWrite(LED_RED,red_state);
  delay(HALF_P_RED*1e03);
}
