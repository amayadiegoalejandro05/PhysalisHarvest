"""Puente local Windows ↔ controlador ROS 2 en WSL ↔ ESP32 por USB."""

import argparse
from contextlib import suppress
from pathlib import Path
import subprocess
import sys
import time

FIRMWARE = "DRV8833_ROS_V1"
PATTERNS = {"F": "1010", "L": "0110", "R": "1001", "S": "0000"}
MOVEMENT = {"CF", "CL", "CR", "F", "L", "R"}
MAX_QUEUE_NS = 125_000_000


def open_link(port):
    # El ESP32 puede tardar en salir del reinicio al abrir USB.
    until = time.monotonic() + 4
    while time.monotonic() < until:
        port.reset_input_buffer()
        port.write(b"ID\n")
        reply = port.readline(80).decode("ascii", errors="replace").strip()
        if reply == FIRMWARE:
            print(reply, flush=True)
            return
        if "_ROS_V" in reply:
            raise RuntimeError(f"Firmware incompatible ({reply}). Carga {FIRMWARE} con VM cortada.")
        time.sleep(0.15)
    raise RuntimeError(
        f"Sin respuesta {FIRMWARE}. Confirma la carga y pulsa EN/RESET con BOOT suelto y VM cortada."
    )


def exchange(port, command):
    port.write((command + "\n").encode("ascii"))
    reply = port.readline(80).decode("ascii", errors="replace").strip()
    expected = {f"OK {command} {PATTERNS[command[-1]]}"}
    if command in MOVEMENT:
        expected.add(f"OK {command} 0000")
    if reply not in expected:
        raise RuntimeError(f"Acuse inesperado para {command}: {reply or 'sin respuesta'}")
    return reply


def read_command(line, now_ns):
    prefix, stamp, deadline, command = line.split()
    if prefix != "CMD" or command not in MOVEMENT | {"S"}:
        raise ValueError("Orden interna inválida")
    if command in MOVEMENT and (
        not -30_000_000 <= now_ns - int(stamp) <= MAX_QUEUE_NS or now_ns >= int(deadline)
    ):
        raise ValueError("Orden vencida. Revisa la latencia y el reloj de Windows/WSL")
    return command


def run(port, args):
    root = Path(__file__).resolve().parents[3]
    shell = (
        "source /opt/ros/jazzy/setup.bash && source install/setup.bash && "
        f"export ROS_DOMAIN_ID={args.domain_id} ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST && "
        "exec ros2 run bench_2wd_drv8833 controller"
    )
    with subprocess.Popen(
        ["wsl.exe", "-d", args.distro, "--cd", str(root / "ros2_ws"), "--", "bash", "-lc", shell],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8",
    ) as controller:
        try:
            last_reply = None
            for line in controller.stdout:
                command = read_command(line, time.time_ns())
                reply = exchange(port, command)
                if reply != last_reply or command == "S":
                    print(reply, flush=True)
                    last_reply = reply
            if controller.wait(timeout=2):
                raise RuntimeError("El controlador ROS terminó. Revisa su diagnóstico en esta terminal.")
        finally:
            try:
                print(exchange(port, "S"), flush=True)
            except (OSError, RuntimeError) as error:
                print(f"Sin acuse de parada. Usa el corte físico. {error}", file=sys.stderr)
            with suppress(OSError):
                controller.stdin.close()
            try:
                controller.wait(timeout=2)
            except subprocess.TimeoutExpired:
                controller.terminate()


def main():
    import serial

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--distro", default="Ubuntu-24.04")
    parser.add_argument("--domain-id", type=int, default=83, choices=range(1, 102), metavar="1..101")
    parser.add_argument("--check", action="store_true", help="Comprueba identidad y parada sin iniciar ROS")
    args = parser.parse_args()
    try:
        with serial.Serial(baudrate=115200, timeout=0.10, write_timeout=0.10) as port:
            port.dtr = port.rts = False
            port.port = args.port
            try:
                port.open()
            except serial.SerialException as error:
                raise RuntimeError(
                    f"No se pudo abrir {args.port}. Confirma el puerto y cierra el Monitor Serie "
                    f"o el puente anterior. Detalle: {error}"
                ) from error
            open_link(port)
            print(exchange(port, "S"), flush=True)
            if not args.check:
                run(port, args)
    except KeyboardInterrupt:
        return 130
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(f"Puente DRV8833 cerrado: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
