# Servo calibration

Status (2026-10-14): **calibrated** — home 1500 µs (level tray), dump_reward 2500 µs (85° counter-clockwise), dump_only 605 µs (85° clockwise), at the owner-approved speed. The Pi still reports undervoltage during some strokes (see below). In production the `crown-crows-detect` service makes one stroke per visit (YES: `dump_reward`, NO: `dump_only`), holds the end position 0.5 s and returns to the centre, where it holds the tray between visits.

## Hardware

- Servo: JAMARA High End Micro 033212, 4.8–6 V, up to 600–750 mA. Already mounted to a tray mechanism, so calibration starts in a narrow range.
- Power: a bench supply at 5.0–6.0 V with a current limit of 1.0–1.2 A. Never the Pi's 5 V pin: the first test from the header caused undervoltage (`0x50005`).
- Wiring, with all power off: servo + to supply +; servo − to supply − **and** Pi GND (physical pin 9); servo signal to GPIO18 (physical pin 12).
- Signal: hardware PWM, enabled once by the owner with `dtoverlay=pwm,pin=18,func=2` in `/boot/firmware/config.txt` and a reboot. The Pi's udev rules give the `gpio` group access to `/sys/class/pwm`, so no root is needed afterwards. Hardware PWM is timed by the PWM peripheral and does not jitter while recognition uses all four CPU cores; `lgpio`'s software-timed servo output would.

## The tool: `servo_bench.py`

One run = one supervised move, then the pulses are switched off.

- Moves only with `--clear` (the operator confirms hands and objects are clear).
- Allowed range 1300–1700 µs by default; anything outside is refused until the operator deliberately passes a wider `--min-us`/`--max-us`. Absolute limits 500–2500 µs.
- Ramps from the last commanded position in 10 µs steps every 40 ms (about 250 µs per second), so a mounted mechanism never jumps.
- Checks `vcgencmd get_throttled` before the move and at every step; any active undervoltage, throttling or capping aborts the move.
- **Holds the position after a move**: the hardware PWM keeps pulsing after the tool exits, so a loaded tray does not fall back. The next move ramps from the position the hardware is holding, read from `/sys/class/pwm`. When pulses are off, the operator must state where the mechanism rests with `--from`; the tool refuses to guess. `--release` switches pulses off on purpose; `--release-after` does so after a single move. On a power problem, an error or Ctrl+C the pulses are switched off to protect the Pi.
- Saves calibrated positions (`home`, `dump_only`, `dump_reward`) to `config/local.servo.json` (Git-ignored); every move is logged to `logs/servo.jsonl`.

Tested against a simulated sysfs PWM directory: all refusals (no `--clear`, unknown start, out of range, unsaved position), the 1500 → 1550 µs ramp in five steps, the written period (20 ms) and duty (1.55 ms), pulses off afterwards, save, go to a saved position and the move log.

## First hardware session — 2026-10-14

- The owner added `dtoverlay=pwm,pin=18,func=2` and rebooted. After the reboot GPIO18 was in PWM0 mode, `/sys/class/pwm/pwmchip0` was writable by the `gpio` group, power flags were `0x0`, and the detector service had started by itself 11 s after boot (the start-at-boot test passed).
- Moves to 1500 µs and 1500 → 1560 µs produced no visible movement and no power flags. Sampling the GPIO18 level read-only during the 1560 µs pulses gave 75 rising edges in 1.5 s and 7.55 % high time, matching 50 Hz and 1.56 ms: the Pi's output was correct.
- The servo was still wired as in the first test: + to the Pi's 5 V (physical pin 4), ground to physical pin 9, signal to physical pin 12. On a move 1560 → 1700 µs the Pi reported active undervoltage (`0x50005`) at 1590 µs; the tool aborted and switched the pulses off within 0.14 s. The owner saw the tray move to about the centre. The flags returned to `0x50000` (historical only) within seconds and the detector service kept running.
- Conclusion: the signal chain and servo work; the Pi's 5 V pin cannot supply the servo. Calibration continues only after the servo + is moved to the bench supply (5.0–6.0 V, 1.0–1.2 A limit), with its − joined to the servo ground and to Pi GND. Last commanded position: 1590 µs.

- Owner observation: without pulses the tray falls back freely to the centre. The first version of the tool switched pulses off after every move and started the next move at the last *recorded* position, so each run began with an unramped jump from the rest position, the moment the undervoltage appeared. The tool now holds position after moves and starts from the held position or the operator-stated rest position.

## Calibration — 2026-10-14

| Position | Pulse | Angle from home (owner's measurement) |
|---|---|---|
| `home` | 1500 µs | 0°, tray level; the tray falls back here without pulses |
| `dump_reward` | 2500 µs | 85° counter-clockwise |
| `dump_only` | 605 µs | 85° clockwise |

- Increasing the pulse width turns the servo counter-clockwise. Which side dumps only and which also rewards does not matter mechanically; the assignment above is a convention.
- At ±1000 µs the servo turned 85° counter-clockwise but 95° clockwise (about 0.085 and 0.095° per µs). The owner chose symmetric 85° strokes, so the clockwise end was shortened to 605 µs, which the owner measured as 85°.
- The tray returned to the same home position in every cycle.
- Speed: the owner judged the first default (about 250 µs/s, 4 s per stroke) too slow. Steps of 40 µs every 10 ms gave 2440–2860 µs/s in practice, 0.35–0.41 s per stroke, which the owner approved; it is now the default. The allowed range now defaults to the calibrated positions (605–2500 µs), so `--goto home`, `--goto dump_only` and `--goto dump_reward` need no extra options.
- Repeat tests, three cycles home → dump_reward → home → dump_only → home with 1 s pauses: at about 1600 µs/s, 12 of 12 moves reached (undervoltage readings during 6 moves, 3 kernel events); at the approved speed with 500 µs, 12 of 12 (2 moves, 1 kernel event); at the approved speed with 605 µs, 12 of 12 (3 moves, 3 kernel events). The Pi recovered each time and the detector service kept running.

### Power: still open

With the servo on the bench supply (5.5 V, 10 mA at rest), the Pi still reports active undervoltage during some strokes, and its kernel logs "Undervoltage detected!" each time. The owner chose to continue; `--warn-power` logs and counts these readings instead of stopping. Without that option the tool still stops at the first reading. Likely causes, not yet checked: the Pi's own supply (the notes mention USB power from ThinkCentre), the servo's return current passing through the Pi's ground pins, or the servo + still also connected to the Pi. Undervoltage can crash the Pi or corrupt its card, so this must be solved before unattended operation. The owner's view (2026-10-14): there was no real power problem; to be discussed later.

## Calibration procedure

Run on the Pi from `~/crown-crows` with the bench supply on and its current display in view.

```bash
python3 -B servo_bench.py --status
```
Shows power flags and anything recorded so far. `/sys/class/pwm/pwmchip0` must exist.

```bash
python3 -B servo_bench.py --move 1520 --from 1500 --clear
```
First move: pulses start at the rest position (about 1500 µs, the centre the tray falls back to) and ramp to 1520; the servo then holds.

```bash
python3 -B servo_bench.py --move 1540 --clear
```
Then 1580, 1620 and so on, then the other direction (1460, 1420, ...). Note which direction tips the tray towards the waste side and which drives the food mechanism. Stop 30–50 µs before any end stop, binding, buzzing, or a current above about 0.5 A while not moving. Go beyond 1300–1700 only on purpose, for example `--min-us 1200 --max-us 1800`.

```bash
python3 -B servo_bench.py --save home
```
After moving to the position you want; likewise `--save dump_only` and `--save dump_reward`. `--goto home --clear` then returns to a saved position.

The `dump_reward` position may only be tested with the food mechanism empty until a portion test is planned.

## Production behaviour (owner's settings, 2026-10-14)

- At start-up the servo moves to the centre (home, 1500 µs): pulses start there if they were off, or it ramps there from a held position.
- On YES it moves to `dump_reward` (2500 µs), on NO to `dump_only` (605 µs), holds the end position for 0.5 s (`--dump-seconds 0.5`) and returns straight to the centre at the approved speed. Measured on the Pi with `selftest.py --servo` (owner watching): 0.31–0.34 s per 85° movement, so a whole stroke takes about 1.15–1.2 s; no undervoltage during the six strokes.

### Energy and power (2026-10-14)

- **Between visits the servo holds the tray at the centre** (`--servo-idle hold`, the default since 2026-10-14). The alternative `--servo-idle release` switches the pulses off at the centre to save the holding current, but only works if the tray stays at the centre without them. On the current setup it drifted away, so each new stroke began with a full-speed jump back to the centre and the Pi reported undervoltage (see [HISTORY](HISTORY.md)). Use `release` only with a mechanism that keeps the tray centred by itself (a spring or a detent).
- After a power-on the position is unknown, so the first pulses at the centre can make the servo jump once.
- A stroke that is interrupted (for example by a service restart) still returns to the centre before the program exits.
- The servo is powered from the Pi's 5 V pin (owner's decision; it stays so). A 2200 µF electrolytic capacitor across its + and − wires was tested on 2026-10-17 and removed: short undervoltage dips began during some tilts with and without it, and a slower ramp (20 µs steps) did not change them either. No stroke has failed ([POWER](POWER.md#measurements-2026-10-17)).
- Each move in `logs/servo.jsonl` records `power_warnings` (steps with any active power flag), `flags_before` (the flags before the move), `undervoltage_readings` (steps with undervoltage) and `dip_started_during_move` (an undervoltage that began during the move, so leftovers from recognition are not blamed on the servo).
- `detect.py --servo-step-us` sets the ramp step (default 40 µs, about 0.4 s per stroke).

## Use by the detector

`detect.py --servo dump|full` drives the calibrated positions through the `Servo` class in `servo_bench.py`. Production runs with `--servo full`: YES → `dump_reward`, NO → `dump_only`, 0.5 s at the end position, back to the centre ([ALGORITHM](ALGORITHM.md#one-visit)).
