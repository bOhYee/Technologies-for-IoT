#include <math.h>

const int TEMP_PIN = A1;
const float B = 4275;
const float R0 = 100000;

void setup() {
  Serial.begin(9600);
  while(!Serial);
  Serial.println("Benvenuto");
}

void loop() {
  int a = analogRead(TEMP_PIN);
  float R = (1023.0 / (float)a) - 1.0;
  R = R * R0;
  float temperature = 1.0/((log(R/R0))/B +1/298.15)-273.15;

  Serial.print("temperature = ");
  Serial.println(temperature);
 
  delay(10*1e03);
}
