import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
from threading import Event
import time

from lights import LIGHTS, StatusLight, open_lights


LOG = logging.getLogger("crown_crows.detect")


def region(frame, tray):
    height, width = frame.shape[:2]
    x0, y0, x1, y1 = tray
    return frame[int(height * y0):int(height * y1), int(width * x0):int(width * x1)]


def tray_rgb(frame, tray, cv2, side=512):
    # The tray area as an RGB image of at most `side` pixels. The model works
    # on 256 x 256 anyway; shrinking first with OpenCV saves about 0.6 s per
    # photo on the Pi 3 compared with handing over the full-resolution area.
    image = region(frame, tray)
    longest = max(image.shape[:2])
    if longest > side:
        scale = side / longest
        image = cv2.resize(image, (max(1, round(image.shape[1] * scale)), max(1, round(image.shape[0] * scale))),
                           interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


# Exposure control. The exposure is metered once at start-up (lights on) and then kept fixed, because
# a fresh auto-exposure per photo costs seconds. Daylight changes the scene by a factor of a hundred,
# so after every photo the brightness of the tray area is measured (a few milliseconds) and the
# exposure for the next photo is corrected; the correction carries over to the next visit.
SHUTTER_MIN_US, SHUTTER_MAX_US, GAIN_MAX = 100, 60000, 8.0
LUMA_TARGET, LUMA_LOW, LUMA_HIGH = 90, 45, 140   # median grey level of the tray (0-255); no change inside LOW..HIGH


# Files in RAM through which the dashboard's server asks for a live photo (it never touches the camera
# or the lights itself; monitor/server.py uses the same names).
SNAPSHOT_REQUEST = Path("/dev/shm/crown-crows-snapshot-request")
SNAPSHOT_IMAGE = Path("/dev/shm/crown-crows-snapshot.jpg")
SNAPSHOT_INFO = Path("/dev/shm/crown-crows-snapshot.json")


def is_paused(path, cache):
    # True while config/local.pause.json (written by the dashboard) says paused. One stat() per call;
    # the file is read again only when it changed.
    try:
        stamp = path.stat().st_mtime_ns
    except OSError:
        cache[:] = [None, False]
        return False
    if cache[0] != stamp:
        try:
            cache[:] = [stamp, bool(json.loads(path.read_text()).get("paused"))]
        except (OSError, ValueError, AttributeError):
            cache[:] = [stamp, False]
    return cache[1]


def tray_brightness(frame, tray, cv2, numpy):
    # Median grey level and share of fully white pixels of the tray area, on every 8th pixel.
    grey = cv2.cvtColor(region(frame, tray)[::8, ::8], cv2.COLOR_BGR2GRAY)
    return float(numpy.median(grey)), float((grey >= 250).mean())


def adapted_exposure(exposure, median, saturated):
    # New exposure for the next photo, or the same one while the picture is in range. A clipped
    # picture does not show how bright the scene really is, so it is cut hard and corrected on the
    # next photo; otherwise the change follows the (gamma 2.2) grey level, at most 8x darker or 4x
    # brighter per step (16x for a nearly black picture). The gain stays at 1 while the shutter can do the job (less noise).
    if saturated > 0.5:
        factor = 1 / 16
    elif saturated > 0.2:
        factor = 1 / 6
    elif LUMA_LOW <= median <= LUMA_HIGH:
        return exposure
    else:
        factor = min(16.0 if median < 20 else 4.0, max(1 / 8, (LUMA_TARGET / max(median, 1.0)) ** 2.2))
    product = exposure["shutter_us"] * exposure["gain"] * factor
    shutter = min(SHUTTER_MAX_US, max(SHUTTER_MIN_US, product))
    gain = min(GAIN_MAX, max(1.0, product / shutter))
    return {**exposure, "shutter_us": int(shutter), "gain": round(gain, 3)}


def camera_arguments(exposure):
    return ["--immediate", "--shutter", str(exposure["shutter_us"]), "--gain", str(exposure["gain"]),
            "--awbgains", f"{exposure['colour_gains'][0]},{exposure['colour_gains'][1]}"]


def meter(options, timeout_ms):
    # Auto-exposure with the lights already on; returns fixed camera settings.
    metadata = Path(f"/dev/shm/crown-crows-exposure-{os.getpid()}.json")
    image = metadata.with_suffix(".jpg")
    try:
        subprocess.run(
            ["rpicam-still", "--nopreview", "--timeout", str(timeout_ms), "--width", "1640", "--height", "1232",
             "--metadata", str(metadata), "--output", str(image)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=options.camera_timeout)
        values = json.loads(metadata.read_text())
    finally:
        metadata.unlink(missing_ok=True)
        image.unlink(missing_ok=True)
    red, blue = values["ColourGains"]
    exposure = {"shutter_us": int(values["ExposureTime"]), "gain": round(values["AnalogueGain"], 3),
                "colour_gains": [round(red, 4), round(blue, 4)]}
    return exposure, camera_arguments(exposure)


def prune(output, keep):
    # Only detect.py batches (<boot>-<sequence>-<pid>) are removed, oldest
    # first, so the SD card cannot fill up during unattended operation.
    batches = sorted((path for path in output.iterdir() if path.is_dir() and path.name.count("-") == 2
                      and len(path.name.split("-")[0]) == 8), key=lambda path: path.stat().st_mtime)
    for batch in batches[:max(0, len(batches) - keep)]:
        shutil.rmtree(batch, ignore_errors=True)


def rotate(path, max_bytes=20_000_000):
    # Keeps a log from growing without limit on a device nobody watches: one
    # older generation (.1) is kept.
    if path.exists() and path.stat().st_size > max_bytes:
        path.replace(path.with_name(path.name + ".1"))


def main():
    options = parse_options()
    rotate(options.log)
    rotate(options.servo_log)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    stop = Event()
    for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(signum, lambda *_: stop.set())
    try:
        started = time.monotonic()
        import cv2
        from recognition import load_model

        cv2.setNumThreads(1)
        recognise = load_model(options.model, options.threads)
        LOG.info("Model loaded in %.1f s", time.monotonic() - started)
        from gpiozero import InputDevice
        from gpiozero.pins.lgpio import LGPIOFactory

        with ExitStack() as stack:
            lock = stack.enter_context((Path.home() / ".crown-crows.lock").open("a"))
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError("Another capture process is already running") from None
            factory = LGPIOFactory()
            stack.callback(factory.close)
            lights = open_lights(stack, factory, options.lights)
            if options.lights == "rgb" and options.status_led == "on":
                lights = StatusLight(lights.channels)
                stack.callback(lights.close)
                lights.set_mode("starting")
            if shutil.which("rpicam-still") is None:
                raise RuntimeError("rpicam-still is not installed")
            # Plain InputDevice: the loop reads the PIR level itself; gpiozero's edge
            # detection would start an lgpio thread that polls constantly
            # (about 5 percent of a core on the Pi 3 while idle).
            sensor = stack.enter_context(InputDevice(17, pull_up=None, active_state=True, pin_factory=factory))
            options.output.mkdir(parents=True, exist_ok=True)
            servo = open_servo(options)
            try:
                with options.log.open("a") as journal:
                    monitor(sensor, lights, recognise, cv2, journal, options, stop, servo)
            except Exception:
                # Show the error on the light for a while before exiting; the
                # service restarts the detector 30 s later.
                LOG.exception("Detection stopped due to an error")
                if hasattr(lights, "set_mode"):
                    lights.set_mode("error")
                    stop.wait(25)
                return 1
        return 0
    except Exception:
        LOG.exception("Detection stopped due to an error")
        return 1


def open_servo(options):
    # Servo use is opt-in (--servo dump|full).
    if options.servo == "off":
        return None
    from servo_bench import Servo

    try:
        servo = Servo(options.pwm_root, options.servo_calibration, options.servo_log, step_us=options.servo_step_us)
        servo.start()
    except Exception as error:
        # A missing calibration or PWM set-up (e.g. on a newly installed Pi)
        # must not stop detection or make the service restart in a loop.
        LOG.error("Servo unavailable, detection continues without strokes: %s", error)
        return None
    if options.servo_idle == "release":
        # The tray rests at home by itself; without pulses the servo uses
        # almost no current between visits.
        time.sleep(.5)
        servo.release()
    LOG.info("Servo mode %s; at home (%d us), %s between visits", options.servo, servo.calibration["home"],
             "released" if options.servo_idle == "release" else "held")
    return servo


def current_accept(options):
    # The threshold can be changed from the dashboard (config/local.accept.json, written by
    # monitor/server.py); it is read at the start of every visit. Without the file, or with an
    # invalid value, --accept applies.
    try:
        value = float(json.loads(options.accept_file.read_text())["accept"])
        return value if 0.3 <= value <= 0.99 else options.accept
    except (OSError, ValueError, KeyError, TypeError):
        return options.accept


def visit(events, boot, triggered, lights, capture, classify, journal, options, stop, servo):
    # Owner's logic (2026-10-14): after the trigger wait --first-delay, then with the light on take up to
    # --photos photos, each one analysed before the next is taken (camera and recognition never compete
    # for the Pi's CPU and supply). The first photo at or above the threshold means YES at once, and the
    # servo makes the reward stroke; if no photo reaches it: NO, dump-only stroke.
    batch = options.output / f"{boot}-{events:04d}-{os.getpid()}"
    batch.mkdir(parents=True)
    results = []
    accept = current_accept(options)
    stop.wait(options.first_delay)
    lights.on()
    try:
        for index in range(1, options.photos + 1):
            if stop.is_set():
                break
            frame, path, exposure = capture(index)
            shutil.copyfile(path, batch / f"image-{index:02d}.jpg")
            started = time.monotonic()
            score, top = classify(frame)
            finished = time.monotonic()
            results.append({"photo": index, "cap_score": round(score, 4), "top_label": top,
                            "analysis_seconds": round(finished - started, 3),
                            "seconds_after_trigger": round(finished - triggered, 3), "exposure": exposure})
            if score >= accept:
                break
    finally:
        lights.off()
    decided = time.monotonic()
    decision = "YES" if results and results[-1]["cap_score"] >= accept else "NO"
    record = {
        "boot": boot,
        "sequence": events,
        "wall_clock_unreliable": datetime.now(timezone.utc).isoformat(),
        "batch": batch.name,
        "photos_taken": len(results),
        "photos": results,
        "accept": accept,
        "decision": decision,
        "trigger_to_decision_seconds": round(decided - triggered, 3),
        "tray": options.tray,
        "model_sha256": options.model_sha256,
    }
    if servo is not None:
        stroke = "dump_reward" if decision == "YES" else "dump_only"
        try:
            servo.dump(stroke, options.dump_seconds, stop=stop)
            if options.servo_idle == "release":
                servo.release()
            record["servo"] = {"stroke": stroke, "outcome": "DONE"}
        except Exception as error:
            # Logged only: the next visit tries again.
            record["servo"] = {"stroke": stroke, "outcome": f"FAILED: {error}"}
            LOG.error("Event %d: servo stroke %s failed: %s", events, stroke, error)
    record["reward"] = decision == "YES" and record.get("servo", {}).get("outcome") == "DONE"
    journal.write(json.dumps(record) + "\n")
    journal.flush()
    best = max(results, key=lambda result: result["cap_score"], default=None)
    LOG.info("Event %d: %s after %d photo(s) in %.2f s from trigger (best cap_score %s, photo %s)%s", events,
             decision, len(results), record["trigger_to_decision_seconds"],
             f"{best['cap_score']:.3f}" if best else "-", best["photo"] if best else "-",
             f"; servo {record['servo']['stroke']} {record['servo']['outcome']}" if "servo" in record else "; servo off")
    prune(options.output, options.keep_batches)
    return servo


def monitor(sensor, lights, recognise, cv2, journal, options, stop, servo=None):
    # The Pi has no real-time clock and runs offline, so batches are named by
    # boot and sequence number; wall-clock time is recorded but unreliable.
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()[:8]
    photo = Path(f"/dev/shm/crown-crows-photo-{os.getpid()}.jpg")  # RAM; only analysed photos are copied to the card
    camera = {}

    def shoot():
        subprocess.run(["rpicam-still", "--nopreview", *camera["args"], "--width", "1640", "--height", "1232",
                        "--output", str(photo)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=options.camera_timeout)
        frame = cv2.imread(str(photo))
        if frame is None:
            raise RuntimeError("Camera produced no readable image")
        return frame

    def capture(index):
        # A photo with the current exposure, then the correction for the next one (see tray_brightness).
        import numpy
        used = camera["exposure"]
        frame = shoot()
        median, saturated = tray_brightness(frame, options.tray, cv2, numpy)
        info = {"shutter_us": used["shutter_us"], "gain": used["gain"], "luma": round(median), "white": round(saturated, 3)}
        new = adapted_exposure(used, median, saturated)
        if (new["shutter_us"], new["gain"]) != (used["shutter_us"], used["gain"]):
            camera["exposure"], camera["args"] = new, camera_arguments(new)
            LOG.info("Exposure adapted: tray grey level %.0f, %.0f %% white: shutter %d us, gain %.2f -> %d us, %.2f",
                     median, saturated * 100, used["shutter_us"], used["gain"], new["shutter_us"], new["gain"])
        return frame, photo, info

    def remeter(timeout_ms=None):
        camera["exposure"], camera["args"] = meter(options, timeout_ms or options.remeter_ms)
        LOG.info("Exposure metered: %s", camera["exposure"])

    def snapshot():
        # A live photo on request: light on for about a second, one photo with the current exposure (which
        # also corrects it), a small copy with the tray area outlined, and the numbers worth seeing when
        # aiming, focusing or checking the light: grey level, white share, sharpness.
        SNAPSHOT_REQUEST.unlink(missing_ok=True)
        info = {"taken_at": time.time()}
        try:
            lights.on()
            try:
                frame, _path, used = capture(0)
            finally:
                lights.off()
            grey = cv2.cvtColor(region(frame, options.tray), cv2.COLOR_BGR2GRAY)
            info.update(used, sharpness=round(float(cv2.Laplacian(grey, cv2.CV_32F).var()), 1))
            small = cv2.resize(frame, (820, 616), interpolation=cv2.INTER_AREA)
            left, top, right, bottom = options.tray
            cv2.rectangle(small, (int(left * 820), int(top * 616)), (int(right * 820), int(bottom * 616)), (0, 255, 0), 2)
            temporary = SNAPSHOT_IMAGE.with_suffix(".tmp.jpg")
            cv2.imwrite(str(temporary), small, [cv2.IMWRITE_JPEG_QUALITY, 80])
            temporary.replace(SNAPSHOT_IMAGE)
        except Exception as error:
            LOG.warning("Live photo failed: %s", error)
            info["error"] = str(error)
        temporary = SNAPSHOT_INFO.with_suffix(".tmp")
        temporary.write_text(json.dumps(info))
        temporary.replace(SNAPSHOT_INFO)
        LOG.info("Live photo taken (requested from the dashboard)")

    def classify(frame):
        # The fixed tray area (--tray), set once per unit: the camera and the
        # tray are mounted rigidly, so no searching is needed.
        result = recognise(tray_rgb(frame, options.tray, cv2))
        return result["cap_score"], max(result["scores"], key=result["scores"].get)

    try:
        # Start-up: meter with the lights on and keep one photo, so aiming and
        # the tray area can be checked after every start.
        lights.on()
        try:
            remeter(2000)
            frame = shoot()
            startup = options.output / f"{boot}-0000-{os.getpid()}"
            startup.mkdir(parents=True)
            shutil.copyfile(photo, startup / "image-01.jpg")
            score, top = classify(frame)
            LOG.info("Start-up tray: cap_score %.3f (top %s), tray area %s", score, top, options.tray)
        finally:
            lights.off()
        LOG.info("PIR warm-up: %.1f seconds; lights off", options.warmup)
        if hasattr(lights, "set_mode"):
            lights.set_mode("warmup")
        if stop.wait(options.warmup):
            return
        if hasattr(lights, "set_mode"):
            if options.servo != "off" and servo is None:
                lights.set_mode("degraded")
            else:
                lights.ready()
        deadline = time.monotonic() + options.run_seconds if options.run_seconds else math.inf
        events = 0
        armed = False
        ready_at = 0.0
        paused, pause_cache = False, [None, False]
        normal_mode = "degraded" if options.servo != "off" and servo is None else "off"
        LOG.info("Ready: waiting for PIR LOW, then a fresh motion event")
        while not stop.is_set() and time.monotonic() < deadline:
            now = time.monotonic()
            if SNAPSHOT_REQUEST.exists():
                snapshot()
            # Pause (dashboard): motion is ignored, so a hand at the tray does not start a visit; the servo
            # keeps holding the tray. Costs one stat() per loop.
            if is_paused(options.pause_file, pause_cache) != paused:
                paused = not paused
                LOG.info("%s", "Paused from the dashboard: motion is ignored" if paused else "Resumed: waiting for a fresh motion event")
                if hasattr(lights, "set_mode"):
                    lights.set_mode("paused" if paused else normal_mode)
            if paused:
                armed = False
                stop.wait(options.poll_seconds)
                continue
            active = sensor.is_active
            if now >= ready_at:
                if not active:
                    armed = True
                elif armed:
                    armed = False
                    events += 1
                    triggered = time.monotonic()
                    LOG.info("Motion: event %d; further triggers ignored for %.0f s", events, options.ignore_seconds)
                    servo = visit(events, boot, triggered, lights, capture, classify, journal, options, stop, servo)
                    ready_at = triggered + options.ignore_seconds
                    if options.cycles and events >= options.cycles:
                        return
            stop.wait(options.poll_seconds)
        LOG.info("Stopped after %d motion event(s)", events)
    finally:
        photo.unlink(missing_ok=True)


def parse_options():
    home = Path.home() / "crown-crows"
    parser = argparse.ArgumentParser(description="Crown Crows detector: PIR-woken photos of the tray, offline "
                                     "recognition of bottle caps and lids, servo stroke to the reward or dump side")
    parser.add_argument("--model", type=Path, required=True, help="model.onnx from export_model.py")
    parser.add_argument("--model-sha256", required=True)
    parser.add_argument("--tray", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"),
                        help="Fixed tray area as fractions of the photo; default: this unit's --tray-file")
    parser.add_argument("--pause-file", type=Path, default=home / "config/local.pause.json",
                        help="While it says {\"paused\": true} (set from the dashboard), motion is ignored")
    parser.add_argument("--accept-file", type=Path, default=home / "config/local.accept.json",
                        help="Threshold set from the dashboard; overrides --accept while present")
    parser.add_argument("--tray-file", type=Path, default=home / "config/local.tray.json",
                        help='Per-unit tray area, {"tray": [X0, Y0, X1, Y1]}, set once (docs/DEPLOY.md); '
                             "without it the whole photo is analysed")
    parser.add_argument("--accept", type=float, default=.6, help="YES when a photo's cap_score reaches this")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--output", type=Path, default=home / "captures")
    parser.add_argument("--log", type=Path, default=home / "logs/detect.jsonl")
    parser.add_argument("--cycles", type=int, default=0, help="Motion events to handle; 0 runs without a limit")
    parser.add_argument("--run-seconds", type=float, default=0, help="0 runs without a time limit")
    parser.add_argument("--warmup", type=float, default=60, help="PIR warm-up after start")
    parser.add_argument("--remeter-ms", type=int, default=1000, help="Auto-exposure time when metering")
    parser.add_argument("--keep-batches", type=int, default=1000, help="Delete the oldest visit photo folders beyond this many")
    parser.add_argument("--camera-timeout", type=float, default=20)
    parser.add_argument("--lights", choices=sorted(LIGHTS), default="rgb", help="Light hardware; see docs/LIGHTING.md")
    parser.add_argument("--photos", type=int, default=3, help="Photos per visit at most (on 167 labelled visits photos 4 and 5 never changed a decision)")
    parser.add_argument("--first-delay", type=float, default=1.0, help="Seconds from the trigger to the first photo")
    parser.add_argument("--ignore-seconds", type=float, default=25.0, help="Triggers are ignored this long after a trigger")
    parser.add_argument("--servo", choices=("off", "dump", "full"), default="off",
                        help="off: no strokes; dump: dump-only stroke after every visit; full: reward stroke for YES")
    parser.add_argument("--servo-calibration", type=Path, default=home / "config/local.servo.json")
    parser.add_argument("--servo-log", type=Path, default=home / "logs/servo.jsonl")
    parser.add_argument("--servo-step-us", type=int, default=40,
                        help="Servo ramp step; smaller steps move more slowly and draw lower current peaks")
    parser.add_argument("--pwm-root", type=Path, default=Path("/sys/class/pwm/pwmchip0"))
    parser.add_argument("--status-led", choices=("on", "off"), default="on",
                        help="Status on the RGB light: blue while starting, three green flashes when ready, then dark; red for problems")
    parser.add_argument("--servo-idle", choices=("hold", "release"), default="hold",
                        help="hold (default): keep the servo at the centre between visits; release: switch its "
                             "pulses off to save energy, only if the tray stays at the centre without them "
                             "(on the first unit it drifted, causing a full-speed jump at the next stroke)")
    parser.add_argument("--poll-seconds", type=float, default=.1,
                        help="How often the PIR is read while idle (0.1 s: about 1 percent CPU instead of 5 at 0.02 s)")
    parser.add_argument("--dump-seconds", type=float, default=.5,
                        help="Hold at the end position before returning to the centre (owner's setting: 0.5 s)")
    options = parser.parse_args()
    if not 1 <= options.photos <= 20:
        parser.error("photos must be 1-20")
    for name in ("warmup", "run_seconds", "camera_timeout", "first_delay", "ignore_seconds"):
        value = getattr(options, name)
        if not math.isfinite(value) or value < 0:
            parser.error(f"{name} must be finite and nonnegative")
    if options.cycles < 0 or options.keep_batches < 1 or not 1 <= options.threads <= 4 or options.remeter_ms < 100 \
            or not 5 <= options.servo_step_us <= 50:
        parser.error("keep-batches must be positive, cycles nonnegative, threads 1-4, remeter-ms at least 100, servo-step-us 5-50")
    if options.camera_timeout <= 0:
        parser.error("camera-timeout must be positive")
    if options.tray is None:
        options.tray = (json.loads(options.tray_file.read_text())["tray"] if options.tray_file.exists()
                        else [0, 0, 1, 1])
    x0, y0, x1, y1 = options.tray
    if not 0 <= x0 < x1 <= 1 or not 0 <= y0 < y1 <= 1:
        parser.error("Tray fractions must satisfy 0 <= X0 < X1 <= 1 and 0 <= Y0 < Y1 <= 1")
    if not 0 < options.accept <= 1:
        parser.error("accept must be in (0, 1]")
    if options.model.suffix != ".onnx":
        parser.error("Model must be the exported .onnx file")
    if hashlib.sha256(options.model.read_bytes()).hexdigest() != options.model_sha256:
        parser.error("Model checksum mismatch")
    options.log.parent.mkdir(parents=True, exist_ok=True)
    return options


if __name__ == "__main__":
    raise SystemExit(main())
