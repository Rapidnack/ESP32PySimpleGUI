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

const int PIN_LEDC = 27;
const int PIN_READ = 36;

void rotateServo(int chan, float angle) { // 0(0.5ms) ~ 180(2.5ms)
  double ms = 0.5 + angle / 90.0;
  int duty = round(ms / 20.0 * 65536.0); // 20ms full scale
  ledcWrite(chan, duty);
}

void mySetup() {
  int ch = 0;
  ledcSetup(ch, 50, 16);
  ledcAttachPin(PIN_LEDC, ch);
  rotateServo(ch, 90);
  analogSetPinAttenuation(PIN_READ, ADC_11db);
  
  displayBuffer[2] = "TCP_LEDC_ADC";
  updateDisplay();
}

void myLoop() {

}

String process(String str) {
  showMessage(str, 0.5);

  if (str.startsWith("angle ")) {
    str = str.substring(str.indexOf(' ') + 1);
    rotateServo(0, str.toFloat());
  } else if (str == "ledcdata") {
    int num = 300;
    int adcBuf[num * 2];
    int pos = 0;
    int n = 0;
    for (int i = 0; i < (num * 10) / 100; i++) { // 10% pre trigger
      adcBuf[pos * 2] = analogRead(PIN_READ);
      adcBuf[pos * 2 + 1] = micros();
      pos = (pos < num - 1) ? pos + 1 : 0;
    }
    while (n < num * 50) {
      int val = analogRead(PIN_READ);
      adcBuf[pos * 2] = val; 
      adcBuf[pos * 2 + 1] = micros();
      pos = (pos < num - 1) ? pos + 1 : 0;
      n++;
      if (val < 0x800) break;
    }
    while (n < num * 50) {
      int val = analogRead(PIN_READ);
      adcBuf[pos * 2] = val; 
      adcBuf[pos * 2 + 1] = micros();
      pos = (pos < num - 1) ? pos + 1 : 0;
      n++;
      if (val >= 0x800) break;
    }
    for (int i = 0; i < (num * 90) / 100; i++) { // 90% post trigger
      adcBuf[pos * 2] = analogRead(PIN_READ);
      adcBuf[pos * 2 + 1] = micros();
      pos = (pos < num - 1) ? pos + 1 : 0;
    }

    String s = String(num * 2);
    for (int i = 0; i < num * 2; i++) {
      s += " " + String(adcBuf[i]);
    }
    return s;
  }

  return "";
}
