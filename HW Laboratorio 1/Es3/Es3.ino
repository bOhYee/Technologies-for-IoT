#include<TimerOne.h>
const int LED = 11;
const int PIR_SENSOR= 7;

int pirValue = LOW;
int ledState = LOW;
volatile int people = 0;


void checkPresence() {  
  pirValue = digitalRead(PIR_SENSOR);
  
  if(pirValue == HIGH){
    ledState=HIGH;
    people++;  
  }
  else{
    ledState=LOW;}
  digitalWrite(LED,ledState);  
}

// Print total number of people detected
void printTotPeople(){
  Serial.print("Total people count: ");
  Serial.println(people);
}

void setup() {
  pinMode(PIR_SENSOR, INPUT);
  pinMode(LED, OUTPUT); 
  
  Serial.begin(9600);
  while(!Serial);
  Serial.println("Benvenuto");
  
  attachInterrupt(digitalPinToInterrupt(PIR_SENSOR), checkPresence, CHANGE);
}


void loop() {
  printTotPeople();
  delay(30*1e03);
}
