#include <Arduino.h>
#include <string.h>

// STBY se habilita externamente. 00 en cada puente deja el motor libre.
constexpr uint8_t pins[] = {25, 26, 27, 14};
constexpr uint32_t watchdogMs = 150;
constexpr uint32_t directionPauseMs = 100;
constexpr uint32_t sessionMs = 8000;

bool armed = false;
uint32_t armedAt = 0;
uint32_t lastContact = 0;
uint32_t stoppedAt = 0;
char requested = 'S';
char active = 'S';
char buffer[16];
size_t length = 0;
bool overflow = false;

void stopOutputs(uint32_t now) {
  for (uint8_t pin : pins) digitalWrite(pin, LOW);
  if (active != 'S') stoppedAt = now;
  active = 'S';
}

void disarm(uint32_t now) {
  stopOutputs(now);
  armed = false;
  requested = 'S';
}

void expire(uint32_t now) {
  if (armed && (now - lastContact >= watchdogMs || now - armedAt >= sessionMs)) {
    disarm(now);
  }
}

void updateMotion(uint32_t now) {
  expire(now);
  if (armed && requested != active) {
    if (active != 'S') {
      stopOutputs(now);
    } else if (now - stoppedAt >= directionPauseMs) {
      digitalWrite(pins[requested == 'L' ? 1 : 0], HIGH);
      digitalWrite(pins[requested == 'R' ? 3 : 2], HIGH);
      active = requested;
    }
  }
}

bool isDirection(char value) {
  return value == 'F' || value == 'L' || value == 'R';
}

void handle(uint32_t now) {
  expire(now);
  buffer[length] = '\0';
  if (!overflow && strcmp(buffer, "ID") == 0) {
    disarm(now);
    Serial.println("DRV8833_ROS_V1");
    return;
  }
  if (!overflow && length == 1 && buffer[0] == 'S') {
    disarm(now);
  } else if (!overflow && length == 2 && buffer[0] == 'C' &&
             isDirection(buffer[1]) && !armed) {
    armed = true;
    requested = buffer[1];
    armedAt = lastContact = now;
  } else if (!overflow && length == 1 && isDirection(buffer[0]) && armed) {
    requested = buffer[0];
    lastContact = now;
  } else {
    disarm(now);
    Serial.println("ERR COMMAND");
    return;
  }
  updateMotion(now);
  Serial.printf("OK %s %d%d%d%d\n", buffer, digitalRead(pins[0]), digitalRead(pins[1]),
                digitalRead(pins[2]), digitalRead(pins[3]));
}

void setup() {
  for (uint8_t pin : pins) {
    digitalWrite(pin, LOW);
    pinMode(pin, OUTPUT);
  }
  disarm(millis());
  Serial.begin(115200);
}

void loop() {
  for (int count = 0; count < 32 && Serial.available(); ++count) {
    const int byte = Serial.read();
    if (byte == '\n') {
      handle(millis());
      length = 0;
      overflow = false;
    } else if (byte != '\r') {
      if (length < sizeof(buffer) - 1) buffer[length++] = byte;
      else overflow = true;
    }
  }
  updateMotion(millis());
  delay(1);
}
