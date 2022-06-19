#include<Bridge.h>
#include<Process.h>
#include <math.h>

// LED variables
const int LED_PIN = 10;

// Temperature sensor variables
const int TEMP_PIN = A1;
const float B = 4275;
const float R0 = 100000;
const int WAIT_TIME = 2000;
Process proc;

float calculateTemperature(int v_read){
    float R;
    float temperature;

    R = (1023.0 / (float) v_read) - 1.0;
    R = R * R0;
    temperature = 1.0/((log(R/R0))/B +1/298.15)-273.15;

    return temperature;
}

void processCommand(String command){
  command.trim();
  if (command.startsWith("L:")== true)
    {
      if (command.endsWith("1")== true)
        analogWrite(LED_PIN,HIGH);
      if (command.endsWith("0")== true)
        analogWrite(LED_PIN,LOW);
      Serial.println(command);
      }
   else {
    Serial.print("Error: ");
    Serial.println(command);
    }
  
}

void setup(){
    Serial.begin(9600);
    while(!Serial);

    Serial.println("Initializing Bridge connection...");
    Bridge.begin();
    Serial.println("Bridge connection established.");
    
    pinMode(LED_PIN,OUTPUT);
    analogWrite(LED_PIN,LOW);
    
    proc.begin("python3");
    proc.addParameter("/root/E03_Lin.py");
    proc.runAsynchronously();
}

void loop(){
    int v_read = analogRead(TEMP_PIN);
    char ret;
    float temp;
    String cmd;

    temp = calculateTemperature(v_read);
    proc.write("T:");
    proc.write(temp);

    while(proc.available() > 0){
        ret = proc.read();
        cmd+=ret;
        processCommand(cmd);
        delay(50);
        cmd[0]='\0';
    }

    delay(WAIT_TIME);
}
