#pragma once

#include <cstdint>
#include <cstdio>
#include <deque>
#include <string>

// MOCK nativo. El reloj y los GPIO son valores en memoria.
constexpr int LOW = 0;
constexpr int HIGH = 1;
constexpr int OUTPUT = 1;
inline uint32_t simulatedMs = 0;
inline int levels[40] = {};
inline uint32_t millis() { return simulatedMs; }
inline void delay(unsigned int) {}
inline void pinMode(int, int) {}
inline void digitalWrite(int pin, int value) { levels[pin] = value; }
inline int digitalRead(int pin) { return levels[pin]; }

struct MockSerial {
  std::deque<char> input;
  std::string output;
  void begin(int) {}
  bool available() { return !input.empty(); }
  int read() {
    const auto value = input.front();
    input.pop_front();
    return value;
  }
  void println(const char* text) { output = std::string(text) + "\n"; }
  template <typename... Args>
  void printf(const char* format, Args... args) {
    char text[128];
    std::snprintf(text, sizeof(text), format, args...);
    output = text;
  }
};

inline MockSerial Serial;
