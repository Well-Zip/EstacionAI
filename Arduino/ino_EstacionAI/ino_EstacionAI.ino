#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>  
#include <ArduinoJson.h>        // Lib JSON
#include <HCSR04.h>				// Lib Ultrasonic



// Configuração do LCD I2C: Endereço 0x27 e 16x2
LiquidCrystal_I2C lcd(0x27, 20, 4);

const char* ssid = "Wes";
const char* password = "12345678";

// URL da API
const char* serverName = "http://192.168.18.14:8000/estacionamento_aespi/info/status";


unsigned long previousMillis = 0;
const long interval = 10000;  


WiFiClient client;

// Variáveis para armazenar os dados da API
int qtd_total_de_vagas = 0;
int qtd_vagas_em_uso = 0;
int qtd_vagas_livres = 0;
String vagas_disponiveis[15];  
int num_vagas_disponiveis = 0; 

//Ultrasonic 
const byte triggerPin = 12; //D6
const byte echoPin = 14; //D5
UltraSonicDistanceSensor distanceSensor(triggerPin, echoPin);

void setup() {
  // Inicializa o LCD com I2C
  //Roxo - D2 - SDA
  // Branco - D1 SCL
  lcd.init();                     
  lcd.backlight();

  Serial.begin(115200);

  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    //Serial.println(" CONECTANDO AO WIFI...");
    lcd.setCursor(5, 0);
    lcd.print("ESTACIONAI");
    lcd.setCursor(1, 2);
    lcd.print("CONECTANDO AO WIFI");
  }
  //Serial.println("CONECTADO AO WIFI");
  lcd.clear();
  lcd.setCursor(5, 0);
  lcd.print("ESTACIONAI");
  lcd.setCursor(3, 2);
  lcd.print("WIFI CONECTADO");
  
  delay(2000);  
  
}

void loop() {
  
  
  unsigned long currentMillis = millis();
  
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis; 

    // Iniciar a requisição HTTP
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      
      
      http.begin(client, serverName);
      int httpCode = http.GET();  // 

      
      if (httpCode > 0) {
        String payload = http.getString();  // Obter a resposta JSON
        //Serial.println(httpCode);
        //Serial.println(payload);

        
        StaticJsonDocument<256> doc;
        
        // Deserializa o JSON recebido
        DeserializationError error = deserializeJson(doc, payload);
        
        if (!error) {
          
          
          qtd_total_de_vagas = doc["qtd_total de vagas"];
          qtd_vagas_em_uso = doc["qtd_vagas_em_uso"];
          qtd_vagas_livres = doc["qtd_vagas_livres"];

          
          num_vagas_disponiveis = 0;
          
          
          JsonArray vagas = doc["vagas_disponiveis"];
          String vagas_formatadas = "";  
          for (int i = 0; i < vagas.size(); i++) {
            vagas_disponiveis[i] = vagas[i].as<String>();
            vagas_formatadas += vagas_disponiveis[i];  
            if (i < vagas.size() - 1) {
              vagas_formatadas += ",";  
            }
            num_vagas_disponiveis++;
          }
          
          // Exibe os dados no Serial Monitor
          
          //Serial.println(qtd_total_de_vagas);
          //Serial.println(qtd_vagas_em_uso);
          //Serial.println(qtd_vagas_livres);
          float distance = distanceSensor.measureDistanceCm();
          //Serial.print("Distancia em cm: ");
          //Serial.println(distance);
          if (distance >= 0 && distance <= 10){
            lcd.backlight();
            lcd.clear();
            lcd.setCursor(5, 0);
            lcd.print("BEM VINDO");
            lcd.setCursor(5, 2);
            lcd.print("ESTACIONAI");

            delay(3000);
            
            lcd.clear();
            lcd.setCursor(5, 0);
            lcd.print("ESTACIONAI");


            lcd.setCursor(0, 1);
            lcd.print("TOTAL DE VAGAS : ");
            
            lcd.setCursor(18, 1);
            lcd.print(qtd_total_de_vagas);

            lcd.setCursor(0, 2);
            lcd.print("VAGAS EM USO   : ");
            
            lcd.setCursor(18, 2);
            lcd.print(qtd_vagas_em_uso);

            lcd.setCursor(0, 3);
            lcd.print("VAGAS LIVRES   : ");
            
            lcd.setCursor(18, 3);
            lcd.print(qtd_vagas_livres);
            delay(4000);

            if(qtd_vagas_livres != 0 ){
              
              lcd.clear();
              lcd.setCursor(5, 0);
              lcd.print("ESTACIONAI   ");
              
              lcd.setCursor(0, 1);
              lcd.print(" VAGAS DISPONIVEIS");


              lcd.setCursor(0, 2);
              lcd.print(vagas_formatadas.substring(0, 20));  
              lcd.setCursor(0, 3);
              lcd.print(vagas_formatadas.substring(21,41));  
              delay(4000);
              lcd.clear();

              //ADicionar Servo Motor Aqui
            }else{
              lcd.clear();
              lcd.setCursor(5, 0);
              lcd.print("ESTACIONAI   ");
              
              lcd.setCursor(5, 2);
              lcd.print("SEM VAGAS");

              lcd.setCursor(4, 3);
              lcd.print("DISPONIVEIS!");

            }

            
          }else{
            lcd.clear();
            lcd.noBacklight();
          }
          
        } else {
          Serial.println("Erro ao parsear JSON");
        }
        
      } else {
        lcd.backlight();
        Serial.println("Erro ao fazer a requisição");
        lcd.clear();
        lcd.setCursor(5, 0);
        lcd.print("ESTACIONAI   ");
        lcd.setCursor(4, 2);
        lcd.print("ERRO NA API!");
      }
      
      http.end();  // Fechar a conexão
    }
  }
}
