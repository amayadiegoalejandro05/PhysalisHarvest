"""Publica observaciones de ArUco recibidas por stdin desde la Astra."""

import json
from math import isfinite
import sys
import time

from geometry_msgs.msg import PointStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from bench_2wd_drv8833.controller import MAX_AGE_NS, TARGET


def message(line):
    stamp, xyz = json.loads(line)
    if type(stamp) is not int:
        raise ValueError("Sello inválido")
    age = time.time_ns() - stamp
    if not -30_000_000 <= age <= MAX_AGE_NS:
        raise ValueError(f"Observación fuera de vigencia ({age / 1e6:.0f} ms)")
    msg = PointStamped()
    msg.header.stamp.sec, msg.header.stamp.nanosec = divmod(stamp, 10**9)
    msg.header.frame_id = "astra_depth_optical_frame"
    if xyz is not None:
        x, y, z = xyz
        if not all(map(isfinite, (x, y, z))) or z <= 0:
            raise ValueError("XYZ inválido")
        msg.point.x, msg.point.y, msg.point.z = map(float, (x, y, z))
    return msg


def main():
    rclpy.init()
    node = Node("bench_2wd_drv8833_aruco")
    try:
        publisher = node.create_publisher(
            PointStamped, TARGET, QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        )
        print("ARUCO_READY", flush=True)
        for line in sys.stdin:
            try:
                publisher.publish(message(line))
            except (ValueError, TypeError, OverflowError) as error:
                node.get_logger().warning(str(error), throttle_duration_sec=2)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
