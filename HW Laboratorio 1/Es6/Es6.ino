#include <math.h>
#include <LiquidCrystal_PCF8574.h>

const int TEMP_PIN = A1;
const float B = 4275;
const float R0 = 100000;
float t1=0;
LiquidCrystal_PCF8574 lcd(0x27);

void setup() {
  lcd.begin(16,2);
  lcd.setBacklight(255);
  lcd.home();
  lcd.clear();
  lcd.print("Temperatura...");
  delay(2*1e03);
}

void loop() {
  int a = analogRead(TEMP_PIN);
  float R = (1023.0 / (float)a) - 1.0;
  R = R * R0;
  float temp = 1.0/((log(R/R0))/B +1/298.15)-273.15;
  //aggiorno la temperatura sul display solo se è diversa da quella impostata al loop precedente
  if(t1!=temp){ 
    t1=temp;
    lcd.clear();
    lcd.print("Temperatura:");
    lcd.print(temp);
    }
  delay(60*1e03);
}
