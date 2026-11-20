"""Control experimental de un ArUco con armado manual y salida por tubería."""

import fcntl
from math import atan2, degrees, isfinite
import os
from pathlib import Path
import sys
import tempfile
from threading import Event, Thread
import time

from geometry_msgs.msg import PointStamped
import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from std_srvs.srv import SetBool


ROOT = "/bench_2wd/drv8833"
TARGET = ROOT + "/aruco_target"
FRAME = "astra_depth_optical_frame"
MAX_AGE_NS = 250_000_000
START_MAX_AGE_NS = 180_000_000
TRACK_MAX_AGE_NS = 450_000_000
FUTURE_NS = 30_000_000
STOP_Z_M = 0.50
WAIT_S = 30.0
DRIVE_S = 7.5


class Controller(Node):
    def __init__(self, disconnected):
        super().__init__("bench_2wd_drv8833_controller")
        self.disconnected = disconnected
        self.target = None
        self.last_stamp = 0
        self.wait_until = self.drive_until = 0.0
        self.turning = False
        self.last_command = None
        self.state = self.create_publisher(String, ROOT + "/state", 10)
        self.create_subscription(
            PointStamped, TARGET, self.receive, QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        )
        self.create_service(SetBool, ROOT + "/enable", self.enable)
        self.create_timer(0.05, self.tick, clock=Clock(clock_type=ClockType.STEADY_TIME))

    def send(self, command, deadline=0):
        print(f"CMD {time.time_ns()} {deadline} {command}", flush=True)

    def report(self, text):
        self.state.publish(String(data=text))
        self.get_logger().info(text)

    def stop(self, reason):
        self.wait_until = self.drive_until = 0.0
        self.turning = False
        self.last_command = None
        self.send("S")
        self.report(f"STOP {reason}")

    def receive(self, msg):
        stamp = msg.header.stamp.sec * 10**9 + msg.header.stamp.nanosec
        xyz = (msg.point.x, msg.point.y, msg.point.z)
        if (
            msg.header.frame_id != FRAME
            or not all(map(isfinite, xyz))
            or xyz[2] <= 0
            or not -FUTURE_NS <= time.time_ns() - stamp <= MAX_AGE_NS
            or stamp <= self.last_stamp
        ):
            self.target = None
            if self.drive_until:
                self.stop("observacion_invalida")
            return
        self.target = (stamp, xyz)
        self.last_stamp = stamp
        if self.drive_until and xyz[2] <= STOP_Z_M:
            self.stop("umbral_z")

    def enable(self, request, response):
        if not request.data:
            self.stop("orden_manual")
            response.success, response.message = True, "Parada solicitada"
        elif self.disconnected.is_set():
            response.success, response.message = False, "Puente desconectado"
        elif self.wait_until or self.drive_until:
            response.success, response.message = False, "Sesión ya armada"
        else:
            self.target = None
            self.wait_until = time.monotonic() + WAIT_S
            self.report("ARMED esperando_aruco")
            response.success, response.message = True, "Armado. Esperando ArUco válido hasta 30 s"
        return response

    def drive(self, now, starting=False):
        stamp, (x, _, z) = self.target
        age_limit = MAX_AGE_NS if starting else TRACK_MAX_AGE_NS
        angle = degrees(atan2(x, z))
        self.turning = abs(angle) > (2.0 if self.turning else 4.0)
        direction = ("L" if angle < 0 else "R") if self.turning else "F"
        if starting:
            self.wait_until = 0.0
            self.drive_until = now + DRIVE_S
        self.send("C" + direction if starting else direction, stamp + age_limit)
        if direction != self.last_command:
            self.report(f"DRIVE {direction} x={x:.3f} z={z:.3f} angulo={angle:.1f}")
            self.last_command = direction

    def tick(self):
        if self.disconnected.is_set():
            raise ExternalShutdownException()
        now = time.monotonic()
        if self.wait_until:
            if now >= self.wait_until:
                self.stop("fin_de_espera")
            elif self.target is not None:
                stamp, xyz = self.target
                if xyz[2] > STOP_Z_M and -FUTURE_NS <= time.time_ns() - stamp <= START_MAX_AGE_NS:
                    self.drive(now, starting=True)
        elif self.drive_until:
            if now >= self.drive_until:
                self.stop("fin_de_sesion")
            elif self.target is None or not -FUTURE_NS <= time.time_ns() - self.target[0] <= TRACK_MAX_AGE_NS:
                self.stop("observacion_vencida")
            else:
                self.drive(now)


def watch_parent(disconnected):
    try:
        # El puente conserva stdin abierto hasta terminar. No hay comandos por stdin.
        os.read(sys.stdin.fileno(), 1)
    finally:
        disconnected.set()


def main():
    domain = int(os.getenv("ROS_DOMAIN_ID", "0"))
    lock = Path(tempfile.gettempdir()) / f"physalis-drv8833-{os.getuid()}-{domain}.lock"
    with lock.open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("Ya hay un controlador DRV8833 en este dominio ROS")
        disconnected = Event()
        Thread(target=watch_parent, args=(disconnected,), daemon=True).start()
        rclpy.init()
        node = Controller(disconnected)
        try:
            rclpy.spin(node)
        except (ExternalShutdownException, KeyboardInterrupt):
            pass
        finally:
            try:
                node.send("S")
            except OSError:
                pass
            node.destroy_node()
            rclpy.try_shutdown()
