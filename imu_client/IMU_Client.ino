// Arduino MKR WiFi 1010 Client Code with IMU - Binary Data
#include <WiFiNINA.h>
#include <MKRIMU.h>
#include "IMU_Client.h"

// WiFi credentials
const char ssid[] = "Tiya’s iPhone";     // Your network SSID
const char pass[] = "yooooooo";  // Your network password

// Server details
const char serverIP[] = "172.20.10.12";  // Your laptop's IP address
const int serverPort = 20905;            // Server port number

WiFiClient client;
led_data_t all_leds[LED_GAME_NUM_LEDS];

void setup() {
    // Initialize serial communication
    Serial.begin(9600);
    while (!Serial);

    // Initialize IMU sensors
    if (!IMU.begin()) {
        Serial.println("Failed to initialize IMU!");
        while (1);
    }
  
    Serial.println("IMU is initialized");

    // Attempt to connect to WiFi network
    Serial.print("Connecting to network: ");
    Serial.println(ssid);

    if (WiFi.status() == WL_NO_MODULE) {
        Serial.println("Communication with WiFi module failed!");
        while (true);
    }

    while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
        Serial.println("Attempting to connect to network...");
        delay(2000);
    }

    Serial.println("Connected to network");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    pinMode(BLUE_BUTTON_PIN, INPUT_PULLUP);
    pinMode(BLUE_LED_PIN, OUTPUT);
    all_leds[BLUE_LED_IDX].led_pin = BLUE_LED_PIN;
    all_leds[BLUE_LED_IDX].button_pin = BLUE_BUTTON_PIN;

    pinMode(GREEN_BUTTON_PIN, INPUT_PULLUP);
    pinMode(GREEN_LED_PIN, OUTPUT);
    all_leds[GREEN_LED_IDX].led_pin = GREEN_LED_PIN;
    all_leds[GREEN_LED_IDX].button_pin = GREEN_BUTTON_PIN;

    pinMode(RED_BUTTON_PIN, INPUT_PULLUP);
    pinMode(RED_LED_PIN, OUTPUT);
    all_leds[RED_LED_IDX].led_pin = RED_LED_PIN;
    all_leds[RED_LED_IDX].button_pin = RED_BUTTON_PIN;

    randomSeed(analogRead(0));
}

void loop() {
    if (!client.connected()) {
        connectToServer();
    }

    if (client.available() >= sizeof(request_t)) {
        handleRequest();
    }

    delay(100);
}

void connectToServer() {
    Serial.println("Connecting to server...");
    if (client.connect(serverIP, serverPort)) {
        Serial.println("Connected to server");
    } else {
        Serial.println("Connection failed");
        delay(5000);
    }
}

void handleRequest() {

    request_t req;
    client.read((uint8_t *)&req, sizeof(req));

    response_t resp;
    resp.type = req.type;

    switch (req.type) {
      case REQ_READ_ACCELERATION:
          if (IMU.accelerationAvailable()) {
              IMU.readAcceleration(resp.u.acc.x, resp.u.acc.y, resp.u.acc.z);
          }
          break;

      case REQ_READ_GYROSCOPE:
          if (IMU.gyroscopeAvailable()) {
              IMU.readGyroscope(resp.u.gyro.x, resp.u.gyro.y, resp.u.gyro.z);
          }
          break;

      case REQ_READ_MAGNETOMETER:
          if (IMU.magneticFieldAvailable()) {
              IMU.readMagneticField(resp.u.mag.x, resp.u.mag.y, resp.u.mag.z);
          }
          break;

      case REQ_START_LED_GAME:
          led_game(&resp);
          break;

      default:
          // Unknown request type, ignore for now
          return;
    }
    client.write((uint8_t *)&resp, sizeof(resp));
}

void led_game(response_t *resp) {
    for (int l = 0; l < LED_GAME_NUM_LEDS; l++) {
        all_leds[l].on_count = 0;
        all_leds[l].success_count = 0;
    }

    for (int i = 0; i < 20; i++) {
        // Randomly select an LED
        int led = random(LED_GAME_NUM_LEDS);
  
        // Generate random ON time between 800 and 1500 millisecs
        int led_on_time = random(800, 1500);
  
        // Turn on the selected LED
        digitalWrite(all_leds[led].led_pin, HIGH);

        all_leds[led].on_count++;
    
        unsigned long start_time = millis();
        while(true) {
            if (digitalRead(all_leds[led].button_pin) == HIGH) {
                all_leds[led].success_count++;
                break;
            }
            if (millis() >= (start_time + led_on_time)) {
                break;
            }
        }
  
        // Turn off the selected LED
        digitalWrite(all_leds[led].led_pin, LOW);
    }

    resp->u.led_game.red_on_count = all_leds[RED_LED_IDX].on_count;
    resp->u.led_game.red_success_count = all_leds[RED_LED_IDX].success_count;

    resp->u.led_game.green_on_count = all_leds[GREEN_LED_IDX].on_count;
    resp->u.led_game.green_success_count = all_leds[GREEN_LED_IDX].success_count;

    resp->u.led_game.blue_on_count = all_leds[BLUE_LED_IDX].on_count;
    resp->u.led_game.blue_success_count = all_leds[BLUE_LED_IDX].success_count;
}
