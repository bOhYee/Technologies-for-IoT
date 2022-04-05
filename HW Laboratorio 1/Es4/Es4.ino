float current_speed = 0;
const int FAN_PIN=13;
// n°step = 5, valore step=51


void setup() {
  pinMode(FAN_PIN, OUTPUT);
  analogWrite(FAN_PIN, current_speed);
  Serial.begin(9600);
  while(!Serial);
  Serial.println("Benvenuto, inizio..");
}


void procInput(){
  int inByte;
  if(Serial.available()>0){
    inByte = Serial.read();
    if(inByte=='+'){//+
       if(current_speed<255){
         current_speed+=51;
         analogWrite(FAN_PIN,(int)current_speed);
         Serial.print("Increasing speed: ");
         Serial.println(current_speed);
         }
       else{
         Serial.println("Already at max speed");
         }  
    }
    if(inByte=='-'){//-
       if(current_speed>0){
         current_speed-=51;
         analogWrite(FAN_PIN,(int)current_speed);
         Serial.print("Decreasing speed: ");
         Serial.println(current_speed);
         }
       else{
         Serial.println("Already at min speed");
         } 
    }
   if(inByte!='\n' && inByte!=45 && inByte!=43)
     Serial.println("Error!");
  }
}

void loop() {
  procInput();
}
