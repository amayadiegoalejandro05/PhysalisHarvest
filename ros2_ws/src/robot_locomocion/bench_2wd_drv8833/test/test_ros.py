"""Prueba ROS 2 de integración con tuberías y sin puente físico."""

from contextlib import contextmanager
import json
import queue
import subprocess
import sys
from threading import Thread
import time

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

from bench_2wd_drv8833.controller import ROOT


@contextmanager
def process(module):
    with subprocess.Popen(
        [sys.executable, "-c", f"from bench_2wd_drv8833.{module} import main; main()"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    ) as child:
        lines = queue.Queue()
        def read_lines():
            for line in child.stdout:
                lines.put(line.strip())

        reader = Thread(target=read_lines, daemon=True)
        reader.start()
        try:
            yield child, lines
        finally:
            child.stdin.close()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
            reader.join(timeout=1)
            assert child.returncode == 0


def test_ros_with_mock_serial_boundary(monkeypatch):
    monkeypatch.setenv("ROS_DOMAIN_ID", "89")
    monkeypatch.setenv("ROS_AUTOMATIC_DISCOVERY_RANGE", "LOCALHOST")
    rclpy.init()
    node = Node("drv8833_mock_test")
    try:
        with process("controller") as (_, commands), process("aruco_source") as (source, ready):
            assert ready.get(timeout=8) == "ARUCO_READY"
            client = node.create_client(SetBool, ROOT + "/enable")
            assert client.wait_for_service(timeout_sec=8)
            seen = []

            def drain():
                while not commands.empty():
                    line = commands.get_nowait()
                    assert len(line.split()) == 4
                    seen.append(line.split()[-1])

            def request(data):
                future = client.call_async(SetBool.Request(data=data))
                rclpy.spin_until_future_complete(node, future, timeout_sec=2)
                assert future.done() and future.result().success

            def feed(xyz, until=None, seconds=0.3):
                end = time.monotonic() + seconds
                seen.clear()
                while time.monotonic() < end:
                    source.stdin.write(json.dumps([time.time_ns(), xyz]) + "\n")
                    source.stdin.flush()
                    time.sleep(0.035)
                    drain()
                    if until in seen:
                        return
                assert until is None, (until, seen)

            # Armar sin cámara acepta la solicitud y no emite movimiento.
            request(True)
            feed(None)
            assert not seen
            feed([0, 0, 0.50])
            assert not seen
            feed([0, 0, 0.80], "CF", 5)
            feed([-0.12, 0, 0.80], "L", 1)
            feed([0.12, 0, 0.80], "R", 1)
            feed([0, 0, 0.80], "F", 1)
            feed([0, 0, 0.50], "S", 1)
            feed([0, 0, 0.80])
            assert not seen

            request(True)
            feed([0, 0, 0.80], "CF", 2)
            feed(None, "S", 1)
            request(True)
            feed([0, 0, 0.80], "CF", 2)
            until = time.monotonic() + 2
            seen.clear()
            while "S" not in seen and time.monotonic() < until:
                time.sleep(0.035)
                drain()
            assert "S" in seen

            request(True)
            request(False)
            time.sleep(0.1)
            drain()
            feed([0, 0, 0.80])
            assert not seen
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
