#include <math.h>
#include <LiquidCrystal_PCF8574.h>
#include <Process.h>
#include <Bridge.h>
LiquidCrystal_PCF8574 lcd(0x27);

Process proc;

const int TEMP_PIN = A1;        // Pin del sensore di temperatura
int temp, minC, maxC, minR, maxR;

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

// PIR
const int PIR_SENSOR=7;          // Pin del sensore PIR
int pirValue = LOW;
int people = 0;                  // Numero di persone rilevate nella stanza

// Microfono
#define N_SOUND_EVENTS 3         // Numero di eventi necessari per rilevare una presenza (in un certo lasso di tempo) col sensore di rumore
#define SOUND_INTERVAL  5        // Lasso di tempo in cui verificare la presenza degli N eventi col sensore di rumore (minuti)
const int MICRO_SENSOR = 2;      // Pin associato al microfono
int events;                      // Eventi rilevati dal microfono

void processCommand(){
    char ret;
    String cmd;
    while(proc.available() > 0){
        ret = proc.read();
        cmd = cmd + String(ret);
    }
    Serial.print("Received command: ");
    Serial.print(cmd);

    // FAN and heater controller
    if(cmd.indexOf("A:") >= 0){
        cmd.replace("A:","");
        if (cmd.toFloat() >= minC)
            current_speed =  51 * (cmd.toFloat() - minC);
        else if(cmd.toFloat() > maxC)
            current_speed = 255;
        else
            current_speed = 0;
        analogWrite(FAN_PIN, current_speed);
            
        if(cmd.toFloat() < minR)
            red_state = 255;
        else if(cmd.toFloat() <= maxR)
            red_state = 51 * (maxR - cmd.toFloat());
        else
            red_state = 0;
        analogWrite(RED_LED, red_state);
    }
    
    if(cmd.indexOf("B:") >= 0){
        cmd.replace("B:","");
        if (cmd.toInt() > 0){
            people = cmd.toInt();
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
    }
    
    else if(cmd.indexOf("E:") >= 0){
        cmd = cmd.charAt(cmd.indexOf("E:")+2);
        if(cmd == "1"){
            Serial.println("Data handling error");
        }
        else if(cmd == "2"){
            Serial.println("Bad request: wrong command syntax");
        }
        else if(cmd == "3"){
            Serial.println("Bad request: missing data");
        }
        else if(cmd == "4"){
            Serial.println("Bad request: command syntax \'<T, P, M>:<number>\'");
        }        
    }
    return;
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
    
    Serial.println("Initializing Bridge connection...");
    Bridge.begin();
    Serial.println("Bridge connection established.");

    proc.begin("python3");
    proc.addParameter("/root/E04_Lin.py");
    proc.runAsynchronously();
   
    Serial.println("Inizio...");
}

void loop() {
    int minC, maxC, minR, maxR;
    char risp;
    float ac, ht;
    unsigned long timePassedMinutes;
  
    int temp = analogRead(TEMP_PIN);
    proc.print("T:");
    proc.println(temp);
  
    // PIR reading
    int foundPir = digitalRead(PIR_SENSOR);
    proc.print("P:");
    proc.print(foundPir);
    
    // microphone reading
    int foundMicro = digitalRead(MICRO_SENSOR);
    proc.print("M:");
    proc.print(foundMicro);
  
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

    while(proc.available() > 0){
        processCommand();
    }
    
    ac = current_speed * 100 / 255;
    ht = red_state * 100 / 255;
    printLCD(temp, people, ac, ht, minC, maxC, minR, maxR);
  
    delay(5*1e03);
}
