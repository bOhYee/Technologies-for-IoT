#include<Bridge.h>
#include<Process.h>
#include <math.h>

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

void setup(){
    Serial.begin(9600);
    while(!Serial);

    Serial.println("Initializing Bridge connection...");
    Bridge.begin();
    Serial.println("Bridge connection established.");

    proc.begin("python3");
    proc.addParameter("/root/lab_3.2.py");
    proc.runAsynchronously();
}

void loop(){
    int v_read = analogRead(TEMP_PIN);
    char ret;
    float temp;

    temp = calculateTemperature(v_read);
    proc.write("T:")
    proc.write(temp);

    while(proc.available() > 0){
        ret = proc.read();
        Serial.print(ret);
    }

    delay(WAIT_TIME);
}
