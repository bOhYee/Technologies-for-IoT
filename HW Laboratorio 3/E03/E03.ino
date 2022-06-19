#include<Bridge.h>
#include<Process.h>
#include <math.h>

// Temperature sensor variables
const int TEMP_PIN = A1;
const float B = 4275;
const float R0 = 100000;
const int WAIT_TIME = 2000;
const int LED_PIN = 10;
Process proc;

float calculateTemperature(int v_read){
    float R;
    float temperature;

    R = (1023.0 / (float) v_read) - 1.0;
    R = R * R0;
    temperature = 1.0/((log(R/R0))/B +1/298.15)-273.15;

    return temperature;
}

void processCommand(){
    char ret;
    String cmd;
    while(proc.available() > 0){
        ret = proc.read();
        cmd = cmd + String(ret);
    }
    Serial.print("Received command: ");
    Serial.print(cmd);
    
    if(cmd.indexOf("L:") >= 0){
        cmd = cmd.charAt(cmd.indexOf("L:")+2);
        if (cmd == "1" || cmd == "0"){
            digitalWrite(LED_PIN, cmd.toInt());
        }
    }
    else if(cmd.indexOf("E:") >= 0){
        cmd = cmd.charAt(cmd.indexOf("E:")+2);
        if(cmd == "1"){
            Serial.println("Cannot convert to float");
        }
        else if(cmd == "2"){
            Serial.println("Bad request: command syntax \'T:<temperature>\'");
        }
        else if(cmd == "3"){
            Serial.println("Bad request: missing data");
        }
        else if(cmd == "4"){
            Serial.println("Bad request: invalid name");
        }
        else if(cmd == "5"){
            Serial.println("Bad request: command syntax \'L:<1, 0>\'");
        }        
    }
    return;
}

void setup(){
    Serial.begin(9600);
    while(!Serial);

    Serial.println("Initializing Bridge connection...");
    Bridge.begin();
    Serial.println("Bridge connection established.");

    proc.begin("python3");
    proc.addParameter("/root/E03_Lin.py");
    proc.runAsynchronously();
}

void loop(){
    int v_read = analogRead(TEMP_PIN);
    float temp = calculateTemperature(v_read);
    String res = "T:" + String(temp);
    Serial.print("Sent command: ");
    Serial.println(res);
    proc.println(res);

    while(proc.available() > 0){
        processCommand();
    }

    delay(WAIT_TIME);
}
