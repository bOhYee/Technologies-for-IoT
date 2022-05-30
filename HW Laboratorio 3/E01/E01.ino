#include<Bridge.h>
#include<BridgeServer.h>
#include<BridgeClient.h>
#include <math.h>

// LED variables
const int LED_PIN = 10;

// Temperature sensor variables
const int TEMP_PIN = A1;
const float B = 4275;
const float R0 = 100000;

// Wait before the next loop
const int WAIT_TIME = 200;

// BridgeServer instance
BridgeServer server;

float calculateTemperature(int v_read){
    float R;
    float temperature;

    R = (1023.0 / (float) v_read) - 1.0;
    R = R * R0;
    temperature = 1.0/((log(R/R0))/B +1/298.15)-273.15;

    return temperature;
}

String createBody(int status, float retVal, char type){

    String body;

    body.concat("{\n");
    body.concat("\"bn\" : \"Yun\",\n");
    body.concat("\"e\" :");
    body.concat("[\n{");
    /*body += "\"n\": ";

    if(type == 'L'){
        body += "\"led\",\n"
    }
    else if(type == 'T'){
        body += "\"temperature\",\n"
    }

    body += "\"t\" : " + String(millis()) + ",\n";
    body += "\"v\" : " + String(retVal) + ",\n";
    body += "\"u\" : ";

    if(type == 'L'){
        body += "\"null\"\n";
    }
    else if(type == 'T'){
        body += "\"Cel\"\n";
    }

    body += "}\n]\n}";*/

    return body;
}

void sendFeedback(BridgeClient client, int status, float retVal, char type){

    String body;

    client.println("Status: " + String(status));
    if(status == 200){
        body = createBody(status, retVal, type);
        client.println(F("Content-type: application/json; charset=utf-8"));
        client.println();
        client.println(body);
    }
}

void processRequest(BridgeClient client){

    int led_val, v_read;
    float temp;
    String command;

    command = client.readStringUntil('/');
    command.trim();
    Serial.print("Command received: ");
    Serial.println(command);

    if(command == "led"){
        led_val = client.parseInt();

        // Set LED status to HIGH or LOW
        if(led_val == 0 || led_val == 1){
            digitalWrite(LED_PIN, led_val);
            sendFeedback(client, 200, led_val, 'L');
        }
        // Malformed URL received
        else{
            sendFeedback(client, 400, -1, 'L');
        }
    }
    else if(command == "temperature"){
        v_read = analogRead(TEMP_PIN);
        temp = calculateTemperature(v_read);
        sendFeedback(client, 200, temp, 'T');
    }
    else{
        sendFeedback(client, 404, -1, 'E');
    }

}

void setup(){
    Serial.begin(9600);
    while(!Serial);

    Serial.println("Initializing Bridge connection...");
    Bridge.begin();
    Serial.println("Bridge connection established.");

    server.listenOnLocalhost();
    server.begin();
    Serial.println("Initialized request management on port 5555...");
}

void loop(){

    BridgeClient client;
    
    client = server.accept();
    if(client != 0){
        processRequest(client);
        client.stop();
    }

    delay(WAIT_TIME);
}
