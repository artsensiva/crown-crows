import argparse
import fcntl
import json
import logging
import math
from pathlib import Path
import signal
import subprocess
import time


LOG = logging.getLogger("crown_crows.servo")

# Absolute limits no command can exceed; the usable range is narrower and
# widened by the operator step by step (--min-us/--max-us).
ABSOLUTE_MIN_US = 500
ABSOLUTE_MAX_US = 2500
PERIOD_NS = 20_000_000
# vcgencmd get_throttled bits that mean a problem right now: under-voltage,
# frequency capped, throttled, soft temperature limit.
ACTIVE_POWER_FLAGS = 0x1 | 0x2 | 0x4 | 0x8


class HardwarePwm:
    # Hardware PWM through sysfs (dtoverlay=pwm,pin=18,func=2 gives pwmchip0
    # channel 0 on GPIO18). Pulses are timed by the PWM peripheral, so CPU load
    # from recognition cannot make the servo jitter.
    def __init__(self, root, channel=0):
        self.chip = Path(root)
        self.pwm = self.chip / f"pwm{channel}"
        self.channel = channel

    def open(self):
        if not self.chip.exists():
            raise RuntimeError(f"{self.chip} missing: is dtoverlay=pwm,pin=18,func=2 active?")
        if not self.pwm.exists():
            (self.chip / "export").write_text(str(self.channel))
            deadline = time.monotonic() + 2
            # udev changes the group of the new files shortly after export.
            while time.monotonic() < deadline:
                try:
                    (self.pwm / "period").write_text(str(PERIOD_NS))
                    break
                except PermissionError:
                    time.sleep(.05)
        (self.pwm / "period").write_text(str(PERIOD_NS))

    def pulse(self, microseconds):
        (self.pwm / "duty_cycle").write_text(str(round(microseconds * 1000)))

    def enable(self, on):
        (self.pwm / "enable").write_text("1" if on else "0")

    def holding(self):
        # Position currently held by the PWM hardware, or None when pulses are
        # off. The hardware keeps pulsing after this program exits.
        try:
            if (self.pwm / "enable").read_text().strip() == "1":
                return round(int((self.pwm / "duty_cycle").read_text()) / 1000)
        except (OSError, ValueError):
            pass
        return None


def power_flags():
    output = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True, check=True, timeout=5).stdout
    return int(output.strip().split("=")[1], 16)


def ramp(start, target, step_us, step_seconds):
    # Positions from start to target in steps of at most step_us.
    steps = max(1, math.ceil(abs(target - start) / step_us))
    return [round(start + (target - start) * index / steps) for index in range(1, steps + 1)]


class Servo:
    # Calibrated servo for automatic use (detect.py): ramps between saved
    # positions at the owner-approved speed, holds after each move, and logs
    # every stroke. It never moves to an uncalibrated pulse width.
    POSITIONS = ("home", "dump_only", "dump_reward")

    def __init__(self, pwm_root, calibration, log, step_us=40, step_seconds=.01, check=power_flags):
        self.pwm = HardwarePwm(pwm_root)
        self.calibration = json.loads(Path(calibration).read_text())
        missing = [name for name in self.POSITIONS if name not in self.calibration]
        if missing:
            raise RuntimeError(f"Servo calibration lacks {missing}; calibrate with servo_bench.py first")
        for name in self.POSITIONS:
            if not ABSOLUTE_MIN_US <= self.calibration[name] <= ABSOLUTE_MAX_US:
                raise RuntimeError(f"Calibrated {name} is outside {ABSOLUTE_MIN_US}-{ABSOLUTE_MAX_US} us")
        self.log = Path(log)
        self.step_us = step_us
        self.step_seconds = step_seconds
        self.check = check

    def start(self):
        # Owner requirement (2026-10-14): the servo goes to the centre (home)
        # when the system starts. Without pulses the tray rests at home, so
        # pulses start there and nothing jumps; if pulses are still on from
        # an earlier run, ramp from the held position to home.
        self.pwm.open()
        self.engage()
        if self.pwm.holding() != self.calibration["home"]:
            self.goto("home")

    def engage(self):
        # Pulses off: the tray rests at home, so pulses start exactly there.
        if self.pwm.holding() is None:
            self.pwm.pulse(self.calibration["home"])
            self.pwm.enable(True)

    def release(self):
        # Energy saving: without pulses the servo draws almost no current and
        # the tray settles at home by itself. Only used at home.
        if self.pwm.holding() == self.calibration["home"]:
            self.pwm.enable(False)

    def goto(self, name, stop=None):
        start = self.pwm.holding()
        if start is None:
            raise RuntimeError("Servo pulses are off; position unknown")
        target = self.calibration[name]
        warnings = 0
        started = time.monotonic()
        reached = start
        for position in ramp(start, target, self.step_us, self.step_seconds):
            if stop is not None and stop.is_set():
                break
            self.pwm.pulse(position)
            reached = position
            time.sleep(self.step_seconds)
            if self.check() & ACTIVE_POWER_FLAGS:
                warnings += 1
        record = {"time_unreliable": time.time(), "source": "detect", "goto": name, "from_us": start,
                  "reached_us": reached, "target_us": target, "seconds": round(time.monotonic() - started, 2),
                  "power_warnings": warnings, "outcome": "REACHED" if reached == target else "STOPPED"}
        with self.log.open("a") as log:
            log.write(json.dumps(record) + "\n")
        if reached != target:
            raise RuntimeError(f"Servo move to {name} stopped at {reached} us")
        return record

    def dump(self, name, dwell=1.0, shake_count=0, shake_us=100, shake_seconds=.12, stop=None):
        # Stroke to a dump position, optionally shake to break friction, wait
        # for the object to fall, then return home. Shaking swings back towards
        # home only, so it never exceeds the calibrated end position.
        self.engage()
        strokes = []
        warnings = 0
        try:
            strokes.append(self.goto(name, stop))
            target = self.calibration[name]
            back = target + (shake_us if self.calibration["home"] > target else -shake_us)
            for _ in range(shake_count):
                if stop is not None and stop.is_set():
                    break
                for position in (back, target):
                    self.pwm.pulse(position)
                    time.sleep(shake_seconds)
                    if self.check() & ACTIVE_POWER_FLAGS:
                        warnings += 1
            if stop is not None:
                stop.wait(dwell)
            else:
                time.sleep(dwell)
        finally:
            # Always return to the centre, also when the service is being
            # stopped mid-stroke (about 0.3 s), so the tray is never left tilted.
            strokes.append(self.goto("home"))
        shake = {"count": shake_count, "us": shake_us, "seconds": shake_seconds, "power_warnings": warnings}
        with self.log.open("a") as log:
            log.write(json.dumps({"time_unreliable": time.time(), "source": "dump", "dump": name, "dwell": dwell,
                                  "shake": shake}) + "\n")
        return {"strokes": strokes, "dwell": dwell, "shake": shake}


def main():
    parser = argparse.ArgumentParser(description="Supervised servo bench tool: one bounded, ramped move per run, then pulses off. Never dispenses on its own.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--move", type=int, metavar="US", help="Move to this pulse width in microseconds")
    action.add_argument("--goto", choices=("home", "dump_only", "dump_reward"), help="Move to a saved calibrated position")
    action.add_argument("--save", choices=("home", "dump_only", "dump_reward"), help="Save the last commanded position under this name")
    action.add_argument("--status", action="store_true", help="Show state, calibration and power flags; no movement")
    action.add_argument("--release", action="store_true", help="Switch the pulses off; the servo stops holding and a loaded mechanism may fall back")
    action.add_argument("--dump-test", choices=("dump_only", "dump_reward"),
                        help="Stroke to a dump position, shake, wait, return home (the servo must be holding)")
    parser.add_argument("--min-us", type=int, help="Lowest allowed pulse; default: the lowest calibrated position, or 1300")
    parser.add_argument("--max-us", type=int, help="Highest allowed pulse; default: the highest calibrated position, or 1700")
    # Owner-approved speed (2026-10-14): about 2400-2900 us/s in practice,
    # 0.35-0.4 s for the 85 degree strokes.
    parser.add_argument("--step-us", type=int, default=40, help="Ramp step")
    parser.add_argument("--step-seconds", type=float, default=.01, help="Time per ramp step")
    parser.add_argument("--hold", type=float, default=.6, help="Settle time at the target before the run ends")
    parser.add_argument("--from", dest="start_us", type=int, metavar="US",
                        help="Where the mechanism physically is when pulses are off (e.g. its rest position); pulses start there")
    parser.add_argument("--release-after", action="store_true", help="Switch pulses off after the move instead of holding")
    parser.add_argument("--clear", action="store_true", required=False, help="Operator confirms hands and objects are clear of the mechanism")
    parser.add_argument("--pwm-root", type=Path, default=Path("/sys/class/pwm/pwmchip0"))
    parser.add_argument("--state", type=Path, default=Path.home() / "crown-crows/logs/servo-state.json")
    parser.add_argument("--calibration", type=Path, default=Path.home() / "crown-crows/config/local.servo.json")
    parser.add_argument("--log", type=Path, default=Path.home() / "crown-crows/logs/servo.jsonl")
    parser.add_argument("--no-power-check", action="store_true", help="Only for offline tests without vcgencmd")
    parser.add_argument("--dwell", type=float, default=1.0, help="Dump test: seconds at the dump position")
    parser.add_argument("--shake-count", type=int, default=0, help="Dump test: number of shakes")
    parser.add_argument("--shake-us", type=int, default=100, help="Dump test: shake amplitude towards home")
    parser.add_argument("--shake-seconds", type=float, default=.12, help="Dump test: time per half swing")
    parser.add_argument("--warn-power", action="store_true",
                        help="Log and count undervoltage instead of stopping. The Pi itself may crash or corrupt its SD card; owner's explicit risk")
    options = parser.parse_args()
    calibration = json.loads(options.calibration.read_text()) if options.calibration.exists() else {}
    positions = [value for key, value in calibration.items() if key in ("home", "dump_only", "dump_reward")]
    if options.min_us is None:
        options.min_us = min(positions + [1300])
    if options.max_us is None:
        options.max_us = max(positions + [1700])
    if not ABSOLUTE_MIN_US <= options.min_us < options.max_us <= ABSOLUTE_MAX_US:
        parser.error(f"Range must lie within {ABSOLUTE_MIN_US}-{ABSOLUTE_MAX_US} us")
    if not 1 <= options.step_us <= 50 or not .01 <= options.step_seconds <= .5 or not 0 <= options.hold <= 3:
        parser.error("step-us 1-50, step-seconds 0.01-0.5, hold 0-3")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    for path in (options.state, options.log, options.calibration):
        path.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(options.state.read_text()) if options.state.exists() else {}
    check = (lambda: 0) if options.no_power_check else power_flags

    pwm = HardwarePwm(options.pwm_root)
    if options.status:
        print(json.dumps({"holding_us": pwm.holding(), "last_commanded_us": state.get("position_us"),
                          "calibration": calibration, "power_flags": hex(check())}, indent=2))
        return 0
    if options.release:
        if pwm.holding() is not None:
            pwm.enable(False)
        LOG.info("Pulses off; the servo no longer holds its position")
        return 0
    if options.dump_test:
        if not options.clear:
            parser.error("Confirm with --clear that hands and objects are clear of the mechanism")
        if not 0 <= options.shake_count <= 20 or not 20 <= options.shake_us <= 300 or not .05 <= options.shake_seconds <= .5 \
                or not 0 <= options.dwell <= 10:
            parser.error("shake-count 0-20, shake-us 20-300, shake-seconds 0.05-0.5, dwell 0-10")
        if pwm.holding() is None:
            parser.error("Pulses are off: first move to home, e.g. --move 1500 --from 1500 --clear")
        servo = Servo(options.pwm_root, options.calibration, options.log, options.step_us, options.step_seconds,
                      (lambda: 0) if options.no_power_check else power_flags)
        servo.pwm.open()
        servo.goto("home")
        result = servo.dump(options.dump_test, options.dwell, options.shake_count, options.shake_us, options.shake_seconds)
        state["position_us"] = servo.calibration["home"]
        options.state.write_text(json.dumps(state) + "\n")
        LOG.info("Dump test %s: dwell %.1f s, %d shake(s) of %d us; back home; power readings during shake: %d",
                 options.dump_test, options.dwell, options.shake_count, options.shake_us, result["shake"]["power_warnings"])
        return 0
    if options.save:
        if "position_us" not in state:
            parser.error("No commanded position recorded yet")
        calibration[options.save] = state["position_us"]
        options.calibration.write_text(json.dumps(calibration, indent=2) + "\n")
        LOG.info("Saved %s = %d us in %s", options.save, state["position_us"], options.calibration)
        return 0

    target = calibration.get(options.goto) if options.goto else options.move
    if target is None:
        parser.error(f"No calibrated position '{options.goto}' saved yet")
    if not options.min_us <= target <= options.max_us:
        parser.error(f"{target} us is outside the allowed range {options.min_us}-{options.max_us}; widen it deliberately")
    if not options.clear:
        parser.error("Confirm with --clear that hands and objects are clear of the mechanism")
    # A servo without pulses does not hold, so a loaded tray falls back to its
    # rest position. Start from the position the hardware is holding; if
    # pulses are off, the operator must say where the mechanism is (--from),
    # otherwise the first pulse would make it jump at full speed.
    held = pwm.holding()
    start = held if held is not None else options.start_us
    if start is None:
        parser.error("Pulses are off, so the position is unknown: pass --from with where the mechanism rests (e.g. 1500)")
    if not options.min_us <= start <= options.max_us:
        parser.error(f"Recorded position {start} us is outside the allowed range; widen the range to include it")

    flags = check()
    if flags & ACTIVE_POWER_FLAGS and not options.warn_power:
        raise SystemExit(f"Power problem before moving (get_throttled {hex(flags)}); not moving")

    stop = []
    for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(signum, lambda *_: stop.append(True))
    lock = (Path.home() / ".crown-crows-servo.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    record = {"time_unreliable": time.time(), "from_us": start, "held_before": held is not None, "target_us": target,
              "goto": options.goto, "flags_before": hex(flags)}
    reached = start
    started = time.monotonic()
    release = options.release_after
    power_warnings = 0
    try:
        pwm.open()
        pwm.pulse(start)
        pwm.enable(True)
        for position in ramp(start, target, options.step_us, options.step_seconds):
            if stop:
                raise KeyboardInterrupt
            pwm.pulse(position)
            reached = position
            time.sleep(options.step_seconds)
            if check() & ACTIVE_POWER_FLAGS:
                if not options.warn_power:
                    raise RuntimeError(f"Power problem during the move at {position} us")
                if not power_warnings:
                    LOG.warning("Undervoltage on the Pi at %d us; continuing because of --warn-power", position)
                power_warnings += 1
        time.sleep(options.hold)
        record["outcome"] = "REACHED"
    except KeyboardInterrupt:
        record["outcome"] = "INTERRUPTED"
        release = True
    except Exception as error:
        # On a power problem or any error, stop driving the servo to protect the Pi.
        record["outcome"] = f"ABORTED: {error}"
        release = True
        raise
    finally:
        try:
            if release:
                pwm.enable(False)
        finally:
            # The last commanded position is recorded even after an abort, so
            # the next run ramps from where the servo was last sent.
            state["position_us"] = reached
            options.state.write_text(json.dumps(state) + "\n")
            flags_after = check()
            record.update({"reached_us": reached, "holding": not release, "seconds": round(time.monotonic() - started, 2),
                           "flags_after": hex(flags_after), "power_warnings": power_warnings,
                           "warn_power": options.warn_power})
            with options.log.open("a") as log:
                log.write(json.dumps(record) + "\n")
            LOG.info("Move %s: %d -> %d us (%s); %s; get_throttled %s; undervoltage readings during move: %d",
                     record.get("outcome"), start, reached, options.goto or "manual",
                     "pulses off" if release else "holding position", hex(flags_after), power_warnings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
