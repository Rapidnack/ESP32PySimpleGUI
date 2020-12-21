#include <Wire.h>
#include "SSD1306Wire.h"
#include <WiFi.h>
#include "Ticker.h"

const char* ssid = "--ssid--"; // 要変更
const char* password = "--password--"; // 要変更
const int socketPort = 54001;
const int socketPort2 = 54002;

void mySetup(); // このスケッチ固有のsetup()
void myLoop(); // このスケッチ固有のloop()
String process(String str); // 受信したメッセージを処理

SSD1306Wire display(0x3c, 21, 22);
String displayBuffer[4];
void updateDisplay() {
  display.clear();
  display.flipScreenVertically();
  display.setFont(ArialMT_Plain_16);
  for (int i = 0; i < 4; i++) {
    display.drawString(0, i * 16, displayBuffer[i]);
  }
  display.display();
}

Ticker messageTimer;
volatile bool updateRequest = false;
void showMessage(String s, float seconds) {
  displayBuffer[3] = s;
  updateDisplay();
  messageTimer.once(seconds, hideMessage);
}
void hideMessage() {
  displayBuffer[3] = "";
  updateRequest = true;
}

WiFiServer server(socketPort);
WiFiServer server2(socketPort2);
WiFiClient client;
WiFiClient client2;

void broadcastEventTXT(String str) {
  if (client2.connected()) {
    client2.println(str);
  }
}

void setup() {
  Serial.begin(57600);
  display.init();

  // このスケッチ固有のsetup()を実行
  mySetup();

  // アクセスポイントに接続
  Serial.println("Connecting");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // TCPサーバーを起動
  server.begin();
  server2.begin();

  Serial.println();
  Serial.println("Server started (" + WiFi.localIP().toString() + ")");
  Serial.println(String(socketPort) + " " + String(socketPort2));

  displayBuffer[0] = WiFi.localIP().toString();
  displayBuffer[1] = String(socketPort) + " " + String(socketPort2);
  updateDisplay();
}

void loop() {
  if (updateRequest) {
    updateRequest = false;
    updateDisplay();
  }

  // このスケッチ固有のloop()を実行
  myLoop();

  if (!client.connected()) {
    client = server.available();
  } else {
    if (client.available()) {
      String inputString = client.readStringUntil('\n');
      inputString.trim();
      String outputString = process(inputString);
      if (outputString != "") {
        client.println(outputString);
      }
    }
  }
  if (!client2.connected()) {
    client2 = server2.available();
  }
}

// 以下、このスケッチ固有の記述

void mySetup() {
  analogSetPinAttenuation(32, ADC_11db);
  analogSetPinAttenuation(33, ADC_11db);
  
  displayBuffer[2] = "TCP_DAC_ADC";
  updateDisplay();
}

void myLoop() {

}

String process(String str) {
  showMessage(str, 0.5);

  if (str.startsWith("dac1 ")) {
    str = str.substring(str.indexOf(' ') + 1);
    dacWrite(25, str.toInt());
  } else if (str.startsWith("dac2 ")) {
    str = str.substring(str.indexOf(' ') + 1);
    dacWrite(26, str.toInt());
  } else if (str == "dacdata") {
    String v32 = String(analogRead(32));
    String ms32 = String(millis());
    String v33 = String(analogRead(33));
    String ms33 = String(millis());
    String s = "4";
    s += " " + v32 + " " + ms32;
    s += " " + v33 + " " + ms33;
    return s;
  }

  return "";
}
