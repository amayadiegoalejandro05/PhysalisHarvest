"""Pruebas del protocolo Windows sin abrir un puerto."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

_spec = spec_from_file_location("bridge", Path(__file__).parents[1] / "drv8833_ros_usb.py")
bridge = module_from_spec(_spec)
_spec.loader.exec_module(bridge)


class MockPort:
    def __init__(self, *replies):
        self.replies = iter(replies)
        self.commands = []

    def reset_input_buffer(self):
        pass

    def write(self, data):
        self.commands.append(data)

    def readline(self, limit):
        return next(self.replies)


class BridgeTests(unittest.TestCase):
    def test_incompatible_firmware(self):
        port = MockPort(b"OTHER_ROS_V2\n")
        with self.assertRaisesRegex(RuntimeError, "Firmware incompatible"):
            bridge.open_link(port)
        self.assertEqual(port.commands, [b"ID\n"])

    def test_interlock_and_invalid_ack(self):
        port = MockPort(b"OK R 0000\n", b"OK R 1001\n", b"OK R 0110\n")
        self.assertEqual(bridge.exchange(port, "R"), "OK R 0000")
        self.assertEqual(bridge.exchange(port, "R"), "OK R 1001")
        with self.assertRaisesRegex(RuntimeError, "Acuse inesperado"):
            bridge.exchange(port, "R")

    def test_deadline_and_queue(self):
        self.assertEqual(bridge.read_command("CMD 100000000 300000000 CF", 125000000), "CF")
        with self.assertRaises(ValueError):
            bridge.read_command("CMD 100000000 110000000 CF", 110000000)
        with self.assertRaises(ValueError):
            bridge.read_command("CMD 100000000 400000000 L", 250000000)
        with self.assertRaises(ValueError):
            bridge.read_command("CMD 100000000 400000000 C", 125000000)
        self.assertEqual(bridge.read_command("CMD 1 0 S", 500000000), "S")
