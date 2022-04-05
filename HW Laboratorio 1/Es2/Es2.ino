#include <TimerOne.h>

const int LED_RED=12;
const int LED_GREEN=11;

const float HALF_P_RED=1.5;
const float HALF_P_GREEN=3.5;

volatile int green_state=LOW;
volatile int red_state=LOW;

void blinkGreen(){
  green_state=!green_state; //inverto lo stato
  digitalWrite(LED_GREEN,green_state);
  }

void serialPrintStatus(){
   int inByte;
  if(Serial.available()>0){
    inByte = Serial.read();

    if(inByte=='R') {
      Serial.print("Led 1 Status: ");
      Serial.println(red_state);
    }
    else if(inByte=='L'){
         Serial.print("Led 2 Status: ");
         Serial.println(green_state);
       }
      
    if(inByte!='\n' && inByte!='R' && inByte!='L')
     Serial.println("Error!");
  }
  }
  
void setup() {
  pinMode(LED_RED,OUTPUT);
  pinMode(LED_GREEN,OUTPUT);
  Timer1.initialize(HALF_P_GREEN*1e06);
  Timer1.attachInterrupt(blinkGreen);

  //messaggio di benvenuto all'avvio
  Serial.begin(9600); //crea una comunicazione serial con baudRate=9600
                     
  while(!Serial); //finchè la connessione non è stata creata
  Serial.println("Benvenuto, inizio..");
}

void loop() {
  red_state=!red_state;
  digitalWrite(LED_RED,red_state);
  delay(HALF_P_RED*1e03);
  serialPrintStatus();
}
