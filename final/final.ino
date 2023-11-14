#include <Servo.h>
#include <TimerOne.h>


int motionSensorPin = 2;
int alarmLedPin = 4;
bool motionDetected = false;
unsigned long lastMotionTime = 0;
const unsigned long timeout = 10000;
bool emailSent = false;

bool notify = false;

// LED and LDR
const int ledPin = 13; 
const int ldrPin = A1; 
//int action = 0; 
bool autoMode = false; 

// Relay and Temperature
const int relayPin = 7;
const int tempPin = A0;
const int relayPin2 = 8;
const int servoPin = 5;
const float tempThreshold = 17.0;

bool motionSensorEnabled = false;
bool lampControlDisabled = false;

Servo myServo;

void timerISR() {
  float temp = readTemperature();
  Serial.println(temp);
  int illum = readLight();
  Serial.println(illum);
  if (notify) {
    Serial.println("ALERT");
    notify = false;
  }
}

void setup() {
  // LED and LDR Setup
  pinMode(ledPin, OUTPUT);
  pinMode(ldrPin, INPUT);
  Serial.begin(9600);
  // 1 - turn on/off, 3 - use automode;

  // Relay and Temperature Setup
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
  pinMode(relayPin2, OUTPUT);
  myServo.attach(servoPin);

  Timer1.initialize(10000000); //10 seconds
  Timer1.attachInterrupt(timerISR);
}

void loop() {

  handleMotionSensor();

  // Process Serial Input
  if (Serial.available() > 0) {
    String action = Serial.readString();
    processInput(action);
  }

  // Auto Mode for LDR
  if (autoMode && !Serial.available()) {
    handleLDR();
  }

  handleTemperature();
  delay(1000);
}

void processInput(String inputAction) {
  if (inputAction == "on") {
    autoMode = false;
    digitalWrite(ledPin, HIGH);
//    Serial.println("The LIGHT is turned ON");
  } else if (inputAction == "off") {
    autoMode = false;
    digitalWrite(ledPin, LOW);
//    Serial.println("The LIGHT is turned OFF");
  } else if (inputAction == "auto") {
    autoMode = true;
//    Serial.println("AUTOMODE");
  } else if (inputAction == "motion_on") {
    motionSensorEnabled = true;
  } else if (inputAction == "motion_off") {
    motionSensorEnabled = false;
    digitalWrite(alarmLedPin, LOW);
  } else if (inputAction == "lamp_on") {
    lampControlDisabled = true;
    digitalWrite(relayPin, LOW);
    digitalWrite(relayPin2, HIGH);
  } else if (inputAction == "lamp_off") {
    lampControlDisabled = true;
    digitalWrite(relayPin, HIGH);
  } else if (inputAction == "lamp_auto") {
    lampControlDisabled = false;
  } else if (inputAction == "cooling_on") {
    lampControlDisabled = true;
    digitalWrite(relayPin, HIGH);
    digitalWrite(relayPin2, LOW);
  } else if (inputAction == "cooling_off") {
    lampControlDisabled = true;
    digitalWrite(relayPin2, HIGH);
  } else if (inputAction == "cooling_auto") {
    lampControlDisabled = false;
  }
}

void handleLDR() {
  int value = readLight();
 // Serial.println(ldrStatus)
  if (value <= 300) {
    digitalWrite(ledPin, HIGH);
//    Serial.println("LDR is DARK, LED is ON");
  } else {
    digitalWrite(ledPin, LOW);
//    Serial.println("---------------");
  }
  delay(1000);
}

void handleTemperature() {
  if (lampControlDisabled) {
     return;
  }

  float temperature = readTemperature();
 // Serial.println(temperature);

  if (temperature < tempThreshold) {
    digitalWrite(relayPin, LOW);
    digitalWrite(relayPin2, HIGH);
  } else if (temperature >= 23) {
    digitalWrite(relayPin, HIGH);
    digitalWrite(relayPin2, LOW);
    myServo.write(180);
    delay(1000);
    myServo.write(0);
    delay(1000);
  }
}

float readTemperature() {
  int analogValue = analogRead(tempPin);
  float milliVolts = (analogValue / 1023.0) * 5000;
  float celsius = milliVolts / 10;
  return celsius;
}

int readLight() {
  return analogRead(ldrPin);
}

void handleMotionSensor() {
  if (!motionSensorEnabled) {
    return;
  }
  if (digitalRead(motionSensorPin) == HIGH) {
    if (!motionDetected) {
      motionDetected = true;
      emailSent = false;
      // Serial.println("Activity found!");
      digitalWrite(alarmLedPin, HIGH);
      lastMotionTime = millis();
    }
  }

  if (motionDetected && (millis() - lastMotionTime > timeout)) {
    motionDetected = false;
    digitalWrite(alarmLedPin, LOW);
    if (!emailSent) {
      sendEmailNotification();
      emailSent = true;
    }
  }
}

void sendEmailNotification() {
  notify = true;
}
