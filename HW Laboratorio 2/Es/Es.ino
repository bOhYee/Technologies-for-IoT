#include <math.h>
#include <LiquidCrystal_PCF8574.h>
LiquidCrystal_PCF8574 lcd(0x27);

const int TEMP_PIN = A1;        // Pin del sensore di temperatura
const float B = 4275;
const float R0 = 100000;

// Motore
#define MIN_SP_C 25             // Temperatura minima a cui azionare la ventola
#define MAX_SP_C 30             // Temperatura massima a cui attribuire velocità massima della ventola
#define MIN_SP_C_pp 22          // Temperatura minima a cui azionare la ventola in presenza di persone
#define MAX_SP_C_pp 27          // Temperatura massima a cui attribuire velocità massima della ventola in presenza di persone
const int FAN_PIN = 13;         // Pin del motorino
int current_speed = 0;          // Velocità della ventola

// LED
#define MIN_SP_R 15             //  Temperatura minima a cui attribuire luminosità massima del LED
#define MAX_SP_R 20             // Temperatura massima a cui azionare il LED
#define MIN_SP_R_pp 18          // Temperatura minima a cui attribuire luminosità massima del LED in presenza di persone
#define MAX_SP_R_pp 23          // Temperatura massima a cui azionare il LED in presenza di persone
const int RED_LED=12;           // pin del LED rosso
int red_state = 0;
const int GREEN_LED=11;         // pin del LED verde
int green_state = 0;

// PIR
#define TIMEOUT_PIR 5            // Tempo di attesa dopo cui ipotizzare che non ci siano più persone in stanza
const int PIR_SENSOR=7;          // Pin del sensore PIR
int pirValue = LOW;
int people = 0;                  // Numero di persone rilevate nella stanza
unsigned long lastPresenceTime = 0;
unsigned long firstPresenceTime = 0;

// Microfono
#define N_SOUND_EVENTS 3         // Numero di eventi necessari per rilevare una presenza (in un certo lasso di tempo) col sensore di rumore
#define SOUND_INTERVAL  5        // Lasso di tempo in cui verificare la presenza degli N eventi col sensore di rumore (minuti)
const int MICRO_SENSOR = 2;      // Pin associato al microfono
int events;                      // Eventi rilevati dal microfono
unsigned long firstEventMicro = 0;
unsigned long lastEventMicro = 0;
#define MAX_CLAP_INTERVAL 1000   // Intervallo massimo tra un battito di mani e l'altro (millisecondi)
#define MIN_CLAP_INTERVAL 300    // Intervallo minimo tra un battito di mani e l'altro (millisecondi)
volatile long currentClap = 0;
volatile long lastClap = 0;
volatile long lastSwitch = 0;

// Calcola la temperatura rilevata dal sensore
int calculateTemperature(){
  int a;
  float R, temperature;

  a = analogRead(TEMP_PIN);
  R = (1023.0 / (float)a) - 1.0;
  R = R * R0;
  temperature = 1.0/((log(R/R0))/B +1/298.15)-273.15;

  return (int) temperature;
}

// Controllo la presenza di persone con il PIR
bool checkPresencePir(){
  bool retValue = false;
  unsigned long timePassedMinutes;

  pirValue = digitalRead(PIR_SENSOR);

  if(pirValue == HIGH){
    retValue = true;
    lastPresenceTime = millis();

    if(firstPresenceTime == 0)
      firstPresenceTime = lastPresenceTime;
  }
  else{
    timePassedMinutes = (lastPresenceTime - firstPresenceTime) / 60000;
    if(timePassedMinutes >= TIMEOUT_PIR){
      firstPresenceTime = 0;
      people = 0;
    }
  }

  return retValue;
}

// Controllo la presenza di persone con il microfono
bool checkPresenceMicrophone(){
  int microValue;
  bool retValue = false;
  unsigned long timePassed;

  microValue = digitalRead(MICRO_SENSOR);
  if(microValue == HIGH){
    events++;
    lastEventMicro = millis();

    if(events >= N_SOUND_EVENTS){
      events = 0;
      retValue = true;
      firstEventMicro = 0;
    }

    if(firstEventMicro == 0)
      firstEventMicro = lastEventMicro;
  }
  else{
    timePassed = (lastEventMicro - firstEventMicro) / 60000;
    if(timePassed >= SOUND_INTERVAL){
      events = 0;
      firstEventMicro = 0;
      lastEventMicro = 0;
    }
  }

  return retValue;
}

// Attiva la ventola a seconda della temperatura rilevata
void activateFan(int temp, int minC, int maxC){

  if (temp >= minC)
    current_speed =  51 * (temp - minC);
  else if(temp > maxC)
    current_speed = 255;
  else
    current_speed = 0;

  analogWrite(FAN_PIN, current_speed);

}

// Accende il diodo in base alla temperatura rilevata
void warmResistor(int temp, int minR, int maxR){

  if(temp < minR)
    red_state = 255;
  else if(temp <= maxR)
     red_state = 51 * (maxR - temp);
  else
     red_state = 0;

  analogWrite(RED_LED, red_state);
}

// Stampa i valori ottenuti su monitor LCD
void printLCD(int temperature, int peopleFound, int ac, int heater, int acMin, int acMax, int heatMin, int heatMax){

  lcd.clear();
  lcd.print("T:");
  lcd.print(temperature);
  lcd.print(" Pres:");
  lcd.print(peopleFound);
  lcd.print("AC:");
  lcd.print(ac);
  lcd.print(" HT:");
  lcd.print(heater);
  delay(5*1e03);            // Attendo 5 secondi prima di scrivere il prossimo messaggio

  lcd.clear();
  lcd.print("AC m:");
  lcd.print(acMin);
  lcd.print(" M:");
  lcd.print(acMax);
  lcd.print("HT m:");
  lcd.print(heatMin);
  lcd.print(" M:");
  lcd.print(heatMax);

}

// Accende/spegne il LED verde in caso di doppio battito di mani
void checkPresenceClap(){
  int microValueC;

  microValueC = digitalRead(MICRO_SENSOR);
  currentClap = millis();

  if(microValueC == HIGH){
    if((currentClap - lastClap < MAX_CLAP_INTERVAL && currentClap - lastClap > MIN_CLAP_INTERVAL && currentClap - lastSwitch > MAX_CLAP_INTERVAL)){
        green_state = !green_state;
        digitalWrite(GREEN_LED,green_state);
        lastSwitch = currentClap;
    }
    lastClap = currentClap;
  }
}

int getValue(){
  char c;
  int value;
  String str;

  while(Serial.available()>0){
    c = Serial.read();
    str += c;
    delay(2);
  }

  value=str.toInt();
  delay(5*1e03);

  return value;
}

void setup() {

  // Inizializzo il monitor seriale
  Serial.begin(9600);
  while(!Serial);
  Serial.println("Benvenuto");

 // Punto 1
 pinMode(FAN_PIN, OUTPUT);
 analogWrite(FAN_PIN, current_speed);
 Serial.println("Motore collegato...");

 // Punto 2
 pinMode(RED_LED,OUTPUT);
 analogWrite(RED_LED,red_state);
 Serial.println("LED rosso collegato...");

 // Punto 3
 pinMode(PIR_SENSOR, INPUT);
 Serial.println("PIR collegato...");

 // Punto 4
 pinMode(MICRO_SENSOR, INPUT);
 Serial.println("Microfono collegato...");

 // Punto 7
 lcd.begin(16,2);
 lcd.setBacklight(255);
 lcd.home();
 lcd.clear();
 lcd.print(" ");
 Serial.println("Monitor LCD collegato...");
 Serial.println("Inizio...");

 // Punto 9
 pinMode(GREEN_LED,OUTPUT);
 analogWrite(GREEN_LED,green_state);
 attachInterrupt(digitalPinToInterrupt(MICRO_SENSOR), checkPresenceClap, CHANGE);
}

void loop() {
  int temp, minC, maxC, minR, maxR;
  char risp;
  float ac, ht;
  bool foundPir, foundMicro;
  unsigned long timePassedMinutes;

  temp = calculateTemperature();
  ac = current_speed * 100 / 255;
  ht = red_state * 100 / 255;

  // Imposto i 4 set-point
  Serial.println("Aggiornare i 4 set-point? y/n");
  if(Serial.available()>0)
    risp = Serial.read();

  delay(5*1e03);
  Serial.print("Hai scelto ");
  Serial.println(risp);

  // Se scrivo 'y' allora devo inserire i dati
  if(risp == 'y'){
    Serial.print("minC: ");
    minC=getValue();
    Serial.print("maxC: ");
    maxC=getValue();
    Serial.print("minR: ");
    minR=getValue();
    Serial.print("maxR: ");
    maxR=getValue();
  }
  else if(people){
      minC = MIN_SP_C_pp;
      maxC = MAX_SP_C_pp;
      minR = MIN_SP_R_pp;
      maxR = MAX_SP_R_pp;
    }
  else{
      minC = MIN_SP_C;
      maxC = MAX_SP_C;
      minR = MIN_SP_R;
      maxR = MAX_SP_R;
  }

  // Gestisco il PIR
  foundPir = checkPresencePir();
  // Gestisco il microfono (commentato per il punto 9)
  //foundMicro = checkPresenceMicrophone();

  // Se ho trovato una presenza o con PIR o con microfono aumento il numero di persone percepite
  if(foundPir)// OR con foundMicro commentato per il punto 9
    people++;

  activateFan(temp, minC, maxC);
  warmResistor(temp, minR, maxR);
  printLCD(temp, people, ac, ht, minC, maxC, minR, maxR);

  delay(5*1e03);
}
