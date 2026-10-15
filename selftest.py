import argparse
import fcntl
import io
import json
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from types import SimpleNamespace


def block_network():
    # Any network use during the self-test is a failure: the Pi must work
    # without external resources.
    def refuse(*args, **kwargs):
        raise RuntimeError("NETWORK ACCESS ATTEMPTED during the self-test")

    socket.socket.connect = refuse
    socket.socket.connect_ex = refuse
    socket.getaddrinfo = refuse
    socket.create_connection = refuse


# Stored tray photos and the decision the visit logic must reach for them.
SCENARIOS = [
    ("crown cap in photo 1", ["crown-cap"] * 5, "YES"),
    ("plastic cap arrives in photo 3", ["empty", "empty", "plastic-cap", "plastic-cap", "plastic-cap"], "YES"),
    ("light-blue cap", ["blue-cap"] * 5, "YES"),
    ("empty tray", ["empty"] * 5, "NO"),
    ("piece of paper", ["paper"] * 5, "NO"),
    ("feather", ["feather"] * 5, "NO"),
]
# Unedited tray photos from the bench unit (grey card, 2026-10-15), kept in
# selftest-photos/ so the test works on any Pi; tray.json holds the tray area
# of these photos. See docs/DEPLOY.md.
PHOTOS = {name: f"selftest-photos/{name}.jpg" for name in ("crown-cap", "plastic-cap", "blue-cap", "empty", "paper", "feather")}


class NoLights:
    def on(self):
        pass

    def off(self):
        pass


def main():
    parser = argparse.ArgumentParser(description="Self-test on the Pi: real camera timing, stored scenario photos, network blocked")
    parser.add_argument("--root", type=Path, default=Path.home() / "crown-crows")
    parser.add_argument("--servo", action="store_true", help="Make the real servo strokes (mechanism must be clear)")
    parser.add_argument("--clear", action="store_true", help="Operator confirms the mechanism is clear (required with --servo)")
    parser.add_argument("--accept", type=float, default=.7)
    options = parser.parse_args()
    if options.servo and not options.clear:
        parser.error("--servo needs --clear")
    block_network()
    sys.path.insert(0, str(options.root))
    import cv2
    import detect
    from recognition import load_model

    lock = (Path.home() / ".crown-crows.lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("The detector service holds the camera: systemctl --user stop crown-crows-detect")
    started = time.monotonic()
    recognise = load_model(options.root / "models/mobileclip2-s0/model.onnx", 4)
    print(f"model loaded in {time.monotonic() - started:.1f} s (stays in memory for all scenarios)")
    cv2.setNumThreads(1)
    images = {name: cv2.imread(str(options.root / path)) for name, path in PHOTOS.items()}
    missing = [name for name, image in images.items() if image is None]
    if missing:
        raise SystemExit(f"Scenario photos missing on this Pi: {missing}")
    servo = None
    if options.servo:
        from servo_bench import Servo

        servo = Servo("/sys/class/pwm/pwmchip0", options.root / "config/local.servo.json", options.root / "logs/servo.jsonl")
        servo.start()
    shot = Path(tempfile.gettempdir()) / "crown-crows-selftest.jpg"
    # Same camera mode as production: exposure metered once, then fixed, so
    # each photo is taken immediately.
    exposure, camera_args = detect.meter(SimpleNamespace(camera_timeout=20), 2000)
    print(f"camera exposure fixed for the run: {exposure}")
    tray = json.loads((options.root / "selftest-photos/tray.json").read_text())["tray"]
    failures = 0
    print(f"{'scenario':26s} {'expected':8s} {'got':4s} {'photos':6s} {'trigger->decision':17s} {'camera':7s} best score")
    for name, sequence, expected in SCENARIOS:
        timings = []

        def capture(index):
            # Real camera call for real timing; the stored scenario photo is
            # analysed in its place so the correct answer is known.
            began = time.monotonic()
            subprocess.run(["rpicam-still", "--nopreview", *camera_args, "--width", "1640", "--height", "1232",
                            "--output", str(shot)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=True, timeout=20)
            timings.append(time.monotonic() - began)
            path = options.root / PHOTOS[sequence[index - 1]]
            return images[sequence[index - 1]], path

        settings = SimpleNamespace(accept=options.accept, photos=5, first_delay=1.0, photo_interval=1.0,
                                   output=Path(tempfile.mkdtemp()), keep_batches=1000, model_sha256="selftest",
                                   tray=tray, dump_seconds=.5)

        def classify(frame):
            result = recognise(cv2.cvtColor(detect.region(frame, tray), cv2.COLOR_BGR2RGB))
            return result["cap_score"], max(result["scores"], key=result["scores"].get)

        journal = io.StringIO()
        detect.visit(1, "selftest", time.monotonic(), NoLights(), capture, classify, journal, settings,
                           threading.Event(), servo)
        record = json.loads(journal.getvalue())
        shutil.rmtree(settings.output, ignore_errors=True)
        best = max((photo["cap_score"] for photo in record["photos"]), default=0)
        ok = record["decision"] == expected
        failures += not ok
        print(f"{name:26s} {expected:8s} {record['decision']:4s} {record['photos_taken']:<6d} "
              f"{record['trigger_to_decision_seconds']:6.2f} s{'':9s} {sum(timings) / len(timings):.2f} s  {best:.3f}"
              f"{'' if ok else '   <-- WRONG'}{'  servo ' + record['servo']['stroke'] + ' ' + record['servo']['outcome'] if 'servo' in record else ''}")
    shot.unlink(missing_ok=True)
    print("network: blocked for the whole run; no access was attempted")
    print("RESULT:", "all scenarios correct" if not failures else f"{failures} scenario(s) wrong")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
