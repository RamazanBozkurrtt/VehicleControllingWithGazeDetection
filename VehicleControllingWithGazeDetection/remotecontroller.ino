#include <WiFi.h>

// Pin tanımlamaları
#define PIN_W 13
#define PIN_S 12
#define PIN_A 14
#define PIN_D 27

const char* ssid = "ESP32_AP";
const char* password = "12345678";

WiFiServer server(5000); // 5000 portunu kullanacağız

void setup() {
  Serial.begin(115200);
  
  // Pinleri çıkış olarak ayarla
  pinMode(PIN_W, OUTPUT);
  pinMode(PIN_A, OUTPUT);
  pinMode(PIN_S, OUTPUT);
  pinMode(PIN_D, OUTPUT);
  
  // Başlangıçta tüm pinleri LOW yap
  digitalWrite(PIN_W, LOW);
  digitalWrite(PIN_A, LOW);
  digitalWrite(PIN_S, LOW);
  digitalWrite(PIN_D, LOW);
  
  // Erişim noktası oluştur
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  
  // TCP sunucusunu başlat
  server.begin();
  Serial.println("TCP server started on port 5000");
}

void loop() {
  WiFiClient client = server.available(); // Gelen bağlantıları dinle
  
  if (client) {
    Serial.println("New client connected");
    
    while (client.connected()) {
      if (client.available()) {
        char command = client.read(); // Gelen komutu oku
        
        // Tüm pinleri önce LOW yapalım
        digitalWrite(PIN_W, LOW);
        digitalWrite(PIN_A, LOW);
        digitalWrite(PIN_S, LOW);
        digitalWrite(PIN_D, LOW);
        
        switch (command) {
          case 'W':
            digitalWrite(PIN_W, HIGH);
            Serial.println("PIN_W HIGH");
            break;
          case 'A':
            digitalWrite(PIN_A, HIGH);
            digitalWrite(PIN_W, HIGH);
            Serial.println("PIN_A HIGH");
            break;
          case 'S':
            digitalWrite(PIN_S, HIGH);
            Serial.println("PIN_S HIGH");
            break;
          case 'D':
            digitalWrite(PIN_D, HIGH);
            digitalWrite(PIN_W, HIGH);
            Serial.println("PIN_D HIGH");
            break;
          case 'O': // OFF komutu
            Serial.println("All pins LOW");
            break;
          default:
            Serial.println("Unknown command");
        }
      }
    }
    
    client.stop();
    Serial.println("Client disconnected");
  }
}