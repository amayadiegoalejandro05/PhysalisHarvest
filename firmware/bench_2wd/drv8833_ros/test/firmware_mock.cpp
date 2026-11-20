#include <cassert>
#include "../drv8833_ros.ino"

void at(uint32_t time) {
  simulatedMs = time;
  loop();
}

std::string command(uint32_t time, const std::string& text) {
  for (char value : text + "\n") Serial.input.push_back(value);
  at(time);
  return Serial.output;
}

int main() {
  setup();
  assert(command(100, "F") == "ERR COMMAND\n");
  assert(command(110, "ID") == "DRV8833_ROS_V1\n");
  assert(command(120, "CF") == "OK CF 1010\n");
  assert(command(130, "L") == "OK L 0000\n");
  at(229);
  assert(active == 'S');
  assert(command(230, "L") == "OK L 0110\n");
  assert(command(240, "R") == "OK R 0000\n");
  assert(command(340, "R") == "OK R 1001\n");
  at(490);
  assert(active == 'S' && !armed);
  assert(command(491, "F") == "ERR COMMAND\n");
  assert(command(600, "CF") == "OK CF 1010\n");
  assert(command(610, "AAAAAAAAAAAAAAAAAAAA") == "ERR COMMAND\n");
  assert(active == 'S' && !armed);
  assert(command(800, "CF") == "OK CF 1010\n");
  for (uint32_t now = 900; now < 8800; now += 100)
    assert(command(now, "F") == "OK F 1010\n");
  assert(command(8800, "F") == "ERR COMMAND\n");
  assert(active == 'S' && !armed);
  assert(command(UINT32_MAX - 50, "CR") == "OK CR 1001\n");
  at(99);
  assert(active == 'S' && !armed);
  assert(command(101, "S") == "OK S 0000\n");
}
