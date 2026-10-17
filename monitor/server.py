"""Read-only monitoring server for Crown Crows (standard library only).

Started by systemd socket activation (deploy/crown-crows-monitor.socket) only
when a browser connects; exits after IDLE_SECONDS without requests, so nothing
runs while nobody is looking. It never writes, never controls hardware and
only serves an allowlist: the page, the two logs from a byte offset on, single
photos, live health readings and recent errors from the system log.
"""
import hmac
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
PAGE = Path(__file__).resolve().parent / "index.html"
LOGS = {"detect": ROOT / "logs/detect.jsonl", "detect.1": ROOT / "logs/detect.jsonl.1",
        "servo": ROOT / "logs/servo.jsonl", "servo.1": ROOT / "logs/servo.jsonl.1"}
CAPTURES = ROOT / "captures"
TOKEN_FILE = ROOT / "config/local.monitor.json"
IDLE_SECONDS = 120
MAX_CHUNK = 4_000_000
BATCH = re.compile(r"^[0-9a-f]{8}-\d{4}-\d+$")
PHOTO = re.compile(r"^image-\d{2}\.jpg$")
THROTTLE_BITS = {0: "undervoltage now", 1: "frequency capped now", 2: "throttled now", 3: "temperature limit now",
                 16: "undervoltage since boot", 17: "frequency capped since boot", 18: "throttled since boot",
                 19: "temperature limit since boot"}


def run(args, timeout=5):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def health():
    flags = run(["vcgencmd", "get_throttled"]).partition("=")[2]
    value = int(flags, 16) if flags else None
    temp = run(["vcgencmd", "measure_temp"]).partition("=")[2].rstrip("'C")
    clock = run(["vcgencmd", "measure_clock", "arm"]).partition("=")[2]
    meminfo = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
    disk = shutil.disk_usage(ROOT)
    service = dict(line.split("=", 1) for line in run(
        ["systemctl", "--user", "show", "crown-crows-detect", "-p", "ActiveState", "-p", "ActiveEnterTimestamp",
         "-p", "NRestarts"]).splitlines() if "=" in line)
    synced = Path("/run/systemd/timesync/synchronized").exists()
    return {
        "read_at": time.time(), "clock_synchronized": synced,
        "uptime_seconds": float(Path("/proc/uptime").read_text().split()[0]),
        "throttled": flags or None,
        "throttled_meaning": [text for bit, text in THROTTLE_BITS.items() if value is not None and value >> bit & 1],
        "temperature_c": float(temp) if temp else None,
        "arm_clock_mhz": round(int(clock) / 1e6) if clock else None,
        "memory_available_mb": round(int(meminfo["MemAvailable"].split()[0]) / 1024),
        "memory_total_mb": round(int(meminfo["MemTotal"].split()[0]) / 1024),
        "disk_free_gb": round(disk.free / 1e9, 1), "disk_total_gb": round(disk.total / 1e9, 1),
        "service_state": service.get("ActiveState"), "service_since": service.get("ActiveEnterTimestamp"),
        "service_restarts": service.get("NRestarts"),
        "captures_visits": sum(1 for path in CAPTURES.iterdir() if BATCH.match(path.name)) if CAPTURES.exists() else 0,
    }


SERVO_SETTINGS = ROOT / "config/local.servo.json"
PWM = Path("/sys/class/pwm/pwmchip0/pwm0")


def last_visit():
    # The last record only: the end of detect.jsonl, a few kilobytes.
    path = LOGS["detect"]
    if not path.exists():
        return None
    with path.open("rb") as handle:
        handle.seek(max(0, path.stat().st_size - 8192))
        lines = handle.read().splitlines()
    for line in reversed(lines):
        try:
            return json.loads(line)
        except ValueError:
            continue
    return None


def now_reading(server):
    # What the box is doing right now, from cheap reads only: GPIO levels
    # (one pinctrl call), the PWM duty cycle, the end of the visit log and the
    # detector's start time (systemctl, at most once a minute). Nothing in the
    # detector is touched.
    reading = {"read_at": time.time()}
    levels = {}
    for line in run(["pinctrl", "get", "17,22,23,27"]).splitlines():
        match = re.match(r"\s*(\d+):.*\|\s*(hi|lo)", line)
        if match:
            levels[int(match.group(1))] = match.group(2) == "hi"
    reading["motion"] = levels.get(17)
    # RGB module, active-low: a channel is lit when its pin is low.
    lit = [not levels[pin] for pin in (27, 22, 23) if pin in levels]
    reading["light"] = None if len(lit) < 3 else ("off" if not any(lit) else "white" if all(lit) else
                                                   "status " + "/".join(name for name, on in zip(("red", "green", "blue"), lit) if on))
    try:
        enabled = (PWM / "enable").read_text().strip() == "1"
        pulse = int((PWM / "duty_cycle").read_text()) // 1000
        positions = json.loads(SERVO_SETTINGS.read_text()) if SERVO_SETTINGS.exists() else {}
        named = [name for name in ("home", "dump_reward", "dump_only")
                 if isinstance(positions.get(name), int) and abs(positions[name] - pulse) <= 30]
        reading["servo"] = {"pulse_us": pulse, "holding": enabled, "position": named[0] if named else "moving"}
    except (OSError, ValueError):
        reading["servo"] = None
    if time.monotonic() - server.service_at > 60:
        info = dict(line.split("=", 1) for line in run(
            ["systemctl", "--user", "show", "crown-crows-detect", "-p", "ActiveState",
             "-p", "ActiveEnterTimestampMonotonic"]).splitlines() if "=" in line)
        server.service_info, server.service_at = info, time.monotonic()
    info = server.service_info
    uptime = float(Path("/proc/uptime").read_text().split()[0])
    started = int(info.get("ActiveEnterTimestampMonotonic", "0") or 0) / 1e6
    running_for = uptime - started if started else None
    visit = last_visit()
    trigger = None
    if visit and visit.get("wall_clock_unreliable") and visit.get("trigger_to_decision_seconds") is not None:
        from datetime import datetime
        trigger = datetime.fromisoformat(visit["wall_clock_unreliable"]).timestamp() - visit["trigger_to_decision_seconds"]
    ignore_left = max(0.0, trigger + 25 - time.time()) if trigger else 0.0
    if info.get("ActiveState") != "active":
        state = f"detector {info.get('ActiveState', 'unknown')}"
    elif running_for is not None and running_for < 75:
        state = f"starting: model, exposure, PIR warm-up (ready in about {75 - running_for:.0f} s)"
    elif reading["light"] == "white":
        state = "visit in progress: taking photos"
    elif ignore_left > 0:
        state = f"visit done; new triggers ignored for {ignore_left:.0f} s"
    else:
        state = "ready: waiting for a crow"
    # System figures from files only (no external programs): well under 1 ms.
    def read_number(path, scale):
        try:
            return round(int(Path(path).read_text()) / scale, 1)
        except (OSError, ValueError):
            return None
    meminfo = {line.split(":")[0]: int(line.split()[1]) for line in Path("/proc/meminfo").read_text().splitlines()[:3]}
    disk = shutil.disk_usage(ROOT)
    reading.update({"cpu_mhz": read_number("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", 1000),
                    "cpu_temp_c": read_number("/sys/class/thermal/thermal_zone0/temp", 1000),
                    "memory_available_mb": round(meminfo.get("MemAvailable", 0) / 1024),
                    "memory_total_mb": round(meminfo.get("MemTotal", 0) / 1024),
                    "disk_free_gb": round(disk.free / 1e9, 1), "disk_total_gb": round(disk.total / 1e9, 1)})
    reading.update({"state": state, "detector_running_seconds": running_for,
                    "load_1min": float(Path("/proc/loadavg").read_text().split()[0]),
                    "last_visit": {key: visit.get(key) for key in ("boot", "sequence", "wall_clock_unreliable",
                                                                   "decision")} if visit else None})
    return reading


def errors():
    service = run(["journalctl", "--user", "-u", "crown-crows-detect", "-p", "warning", "-n", "50", "-o",
                   "short-iso", "--no-pager"], timeout=15)
    kernel = run(["journalctl", "-k", "--no-pager", "-o", "short-iso", "--grep", "Undervoltage detected"], timeout=15)
    lines = lambda text: [line for line in text.splitlines() if line and not line.startswith("--")]
    return {"service": lines(service)[-50:], "kernel_undervoltage": lines(kernel)[-500:]}


class Handler(BaseHTTPRequestHandler):
    server_version = "crown-crows-monitor"

    def log_message(self, *args):
        pass

    def send(self, status, body, kind="application/json", headers=None):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def fail(self, status, message):
        self.send(status, json.dumps({"error": message}).encode())

    def do_GET(self):
        self.server.last_request = time.monotonic()
        url = urlparse(self.path)
        query = {key: values[0] for key, values in parse_qs(url.query).items()}
        if url.path in ("/", "/index.html"):
            return self.send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if not url.path.startswith("/api/"):
            return self.fail(404, "not found")
        if not self.server.token or not hmac.compare_digest(self.headers.get("X-Token", ""), self.server.token):
            return self.fail(401, "token required")
        try:
            if url.path == "/api/log":
                path = LOGS.get(query.get("name", ""))
                if path is None:
                    return self.fail(400, "unknown log")
                if not path.exists():
                    return self.send(200, b"", "text/plain", {"X-Size": "0", "X-Inode": "0"})
                offset = int(query.get("from", "0"))
                stat = path.stat()
                if offset < 0 or offset > stat.st_size:
                    offset = 0
                with path.open("rb") as handle:
                    handle.seek(offset)
                    data = handle.read(MAX_CHUNK)
                cut = data.rfind(b"\n") + 1  # whole lines only
                return self.send(200, data[:cut], "text/plain; charset=utf-8",
                                 {"X-Size": str(stat.st_size), "X-Inode": str(stat.st_ino),
                                  "X-Next": str(offset + cut)})
            if url.path == "/api/photo":
                batch, name = query.get("batch", ""), query.get("file", "")
                if not BATCH.match(batch) or not PHOTO.match(name):
                    return self.fail(400, "invalid photo")
                path = CAPTURES / batch / name
                if not path.is_file():
                    return self.fail(404, "photo not kept")
                return self.send(200, path.read_bytes(), "image/jpeg")
            if url.path == "/api/health":
                now = time.monotonic()
                if now - self.server.health_at > 10:
                    self.server.health_cache, self.server.health_at = health(), now
                return self.send(200, json.dumps(self.server.health_cache).encode())
            if url.path == "/api/now":
                return self.send(200, json.dumps(now_reading(self.server)).encode())
            if url.path == "/api/errors":
                return self.send(200, json.dumps(errors()).encode())
            return self.fail(404, "not found")
        except (OSError, ValueError) as error:
            return self.fail(500, type(error).__name__)


def main():
    token = json.loads(TOKEN_FILE.read_text()).get("token", "") if TOKEN_FILE.exists() else ""
    if os.environ.get("LISTEN_FDS") == "1" and os.environ.get("LISTEN_PID") == str(os.getpid()):
        server = HTTPServer(("", 0), Handler, bind_and_activate=False)
        server.socket = socket.socket(fileno=3)
    else:  # manual start for testing: python monitor/server.py [port]
        server = HTTPServer(("", int(sys.argv[1]) if len(sys.argv) > 1 else 8080), Handler)
    server.token, server.health_at, server.health_cache = token, 0.0, {}
    server.service_at, server.service_info = -1e9, {}
    server.last_request = time.monotonic()
    server.timeout = 5
    while time.monotonic() - server.last_request < IDLE_SECONDS:
        server.handle_request()


if __name__ == "__main__":
    main()
