#!/usr/bin/env python3
"""Start the packaged ARM64 Valetudo with its mock robot and check HTTP."""
import argparse
import base64
import http.client
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import tempfile
import time


def get_version(port, authorization=None):
    client = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        headers = {"Authorization": authorization} if authorization is not None else {}
        client.request("GET", "/api/v2/valetudo/version", headers=headers)
        response = client.getresponse()
        return response.status, response.read(4096)
    finally:
        client.close()


def require_startup(process, port, commit):
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Packaged Valetudo exited with code {process.returncode}")
        try:
            status, _ = get_version(port)
        except (ConnectionError, TimeoutError):
            time.sleep(0.25)
            continue
        if status != 401:
            raise RuntimeError(f"Expected HTTP 401 before authentication, got {status}")
        auth = "Basic " + base64.b64encode(b"smoke:local-only").decode("ascii")
        status, body = get_version(port, auth)
        if status != 200:
            raise RuntimeError(f"Authenticated version request returned HTTP {status}")
        version = json.loads(body)
        if not isinstance(version.get("release"), str) or version.get("commit") != commit:
            raise RuntimeError("Packaged version metadata did not match the build")
        if process.poll() is not None:
            raise RuntimeError("Packaged Valetudo exited during the HTTP check")
        return
    raise RuntimeError("Packaged Valetudo did not open its web port within 40 seconds")


def smoke(command, commit):
    defaults = Path(__file__).resolve().parents[1] / "backend/lib/res/default_config.json"
    config = json.loads(defaults.read_text(encoding="utf-8"))
    config["embedded"] = False
    config["robot"]["implementation"] = "MockValetudoRobot"
    config["webserver"]["basicAuth"] = {"enabled": True, "username": "smoke", "password": "local-only"}
    for setting in ("mqtt", "ntpClient", "networkAdvertisement", "updater"):
        config[setting]["enabled"] = False
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    config["webserver"]["port"] = port

    with tempfile.TemporaryDirectory(prefix="valetudo-arm64-smoke-") as folder:
        work = Path(folder)
        (work / "data").mkdir()
        (work / "config.json").write_text(json.dumps(config), encoding="utf-8")
        env = {"PATH": os.environ["PATH"], "HOME": folder,
               "VALETUDO_CONFIG_PATH": str(work / "config.json"),
               "VALETUDO_DATA_PATH": str(work / "data"),
               "VALETUDO_LOG_PATH": str(work / "valetudo.log")}
        with (work / "console.log").open("w+b") as console:
            with subprocess.Popen(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                  stdout=console, stderr=subprocess.STDOUT) as process:
                try:
                    require_startup(process, port, commit)
                except (OSError, RuntimeError, ValueError, http.client.HTTPException):
                    console.seek(0)
                    print(console.read(8192).decode("utf-8", errors="replace"), flush=True)
                    raise
                finally:
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--emulator", default="qemu-aarch64")
    args = parser.parse_args()
    command = [str(args.binary.resolve(strict=True))]
    if platform.machine() not in ("aarch64", "arm64"):
        command.insert(0, args.emulator)
    smoke(command, args.commit)
    print("Packaged ARM64 startup and authenticated HTTP version check passed.")


if __name__ == "__main__":
    main()
