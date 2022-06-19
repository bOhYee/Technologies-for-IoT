#include <Bridge.h>
#include <BridgeServer.h>
#include <BridgeClient.h>
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
    if(status == 200){
      body.concat("{");
      body.concat("\"bn\" : \"Yun\",");
      body.concat("\"e\" :");
      body.concat("[{");
      body += "\"n\": ";
      if(type == 'L'){
          body += "\"led\",";
      }
      else if(type == 'T'){
          body += "\"temperature\",";
      }
      body += "\"t\" : " + String(millis()) + ",";
      body += "\"v\" : " + String(retVal) + ",";
      body += "\"u\" : ";
      if(type == 'L'){
          body += "\"null\"";
      }
      else if(type == 'T'){
          body += "\"Cel\"";
      }
      body += "}]}";
    }
    else{
      body.concat("{\"errorCode\": " + String(status) + ", ");
      body.concat("\"errorText\": ");
      if(status == 400){
        body.concat("\"Bad request: the LED can only be turned on (1) or off (0).\"}");
      }
      else if(status == 404){
        body.concat("\"Not found: the available services are /led/<1, 0>/ and /temperature/.\"}");
      }
    }
    return body;
}

void sendFeedback(BridgeClient client, int status, float retVal, char type){

    String body = createBody(status, retVal, type);

    //Positive response
    if(status == 200){
        client.println("HTTP/1.1 200 OK ");
    }
    //Negative response
    else{
        client.print("HTTP/1.1 ");
        client.print(status);
        client.print(" KO ");
    }
    client.println("Content-Type: application/json; charset=utf-8 ");
    client.println("Server: Arduino ");
    client.println();
    client.println(body);
    client.println();
}

void processRequest(BridgeClient client){

    int led_val, v_read;
    float temp;
    String command;
    
    command = client.readString();
    command.trim();
    Serial.print("Command received: ");
    Serial.println(command);
    
    if(command.indexOf("/led") > 0){
        command = command.substring(command.indexOf("/led")+5, command.indexOf("/led")+6);
        led_val = command.toInt();

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
    else if(command.indexOf("/temperature") > 0){
        v_read = analogRead(TEMP_PIN);
        temp = calculateTemperature(v_read);
        Serial.println(temp);
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
    
    pinMode(LED_PIN,OUTPUT);
    analogWrite(LED_PIN,LOW);

    server.noListenOnLocalhost();
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
