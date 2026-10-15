# Crown Crows

**A self-contained Raspberry Pi system that invites crows to clean up bottle caps and lids, and rewards them with food.**

**Mission: mutual aid between birds, nature and people.** Crows are clever enough to learn a trade: bring a bottle cap or lid, get a small food reward. Crown Crows is a cheap, fully documented, battery-powered box that makes that trade fair and automatic, and puts the birds' well-being first. The name plays on the *crown cap* (German *Kronkorken*) and on crowning the crows for a good deed. Background, prior work and research directions: [MISSION](docs/MISSION.md).

A crow drops an object into a small intake. A camera looks at it, an on-device vision model decides whether it is a bottle cap or lid, and a servo tips the tray one way or the other: a cap goes into a closed waste container **and the crow gets a food reward**; anything else goes into the container without a reward. Everything runs locally on a Raspberry Pi 3, with no network connection, no cloud service and no custom-trained model.

> **Birds first.** An earlier version of this device was built around a kind of litter that, we later realised, could harm the birds carrying it. We had focused on the technology and underestimated the risk to the birds. That was a significant mistake. We withdrew the design and rebuilt the project around objects that are safe for crows: bottle caps and lids are not toxic and too large to swallow.

> **Status (October 2026): bench prototype.** The detection loop, recognition, servo strokes, installer and self-test run on the Pi. Recognition of caps was tested on a first bench session; the grey tray, the final threshold, the mechanical housing, the food dispenser and outdoor trials are the next steps ([ROADMAP](docs/ROADMAP.md)).

---

## Contents

- [How it works](#how-it-works)
- [Status light](#status-light)
- [Results](#results)
- [Hardware](#hardware)
- [Software](#software)
- [Recognition without training](#recognition-without-training)
- [Engineering challenges solved](#engineering-challenges-solved)
- [Energy and autonomy](#energy-and-autonomy)
- [Install it yourself](#install-it-yourself)
- [Operating it](#operating-it)
- [Repository layout](#repository-layout)
- [Limitations and next steps](#limitations-and-next-steps)
- [Ethics and safety](#ethics-and-safety)
- [Documentation](#documentation)

---

## How it works

```
 crow lands           PIR motion sensor fires
      │                        │
      ▼                        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ 1 s pause → light on → up to 5 photos, 1 s apart            │
 │ each photo is analysed in the background as soon as taken   │
 └─────────────────────────────────────────────────────────────┘
      │ any photo scores ≥ 0.6 as "cap or lid"?
      ├── YES (stop at once) ──► servo 85° counter-clockwise:
      │                          tray into waste + food reward
      └── NO  (after 5 photos) ► servo 85° clockwise:
                                 tray into waste, no reward
      │
      ▼  servo holds 0.5 s, returns to the centre
 further triggers ignored for 25 s (the crow eats and leaves)
```

1. **Wake-up.** A passive-infrared (PIR) sensor aimed at the intake opening detects the crow's head. A PIR reacts only to warm moving bodies, so the camera, not the PIR, decides what was deposited.
2. **Photos.** After a 1 s pause (the crow needs a moment to let go), the box's own light switches on and the camera takes up to five photos, one per second.
3. **Pipelined recognition.** Each photo is analysed in a background thread while the next is being taken. Only the unit's fixed tray area is analysed.
4. **Decision.** The first photo scoring at least **0.6** for "cap or lid" ends the sequence with **YES**. If none of the five does, the answer is **NO**.
5. **Action.** The servo turns 85° to the reward side (YES) or the dump side (NO), holds 0.5 s, and returns to the centre, where it holds the tray until the next visit.
6. **Record.** Every visit is logged with all photo scores, the decision, the timing and the servo stroke; the photos are kept up to a size limit.

At start-up the servo moves to the centre, the camera measures its exposure once, and the motion sensor warms up for 60 s; the box is ready about 2 minutes after power-on. Details: [ALGORITHM](docs/ALGORITHM.md).

## Status light

The RGB light that illuminates the tray for photos also shows the start-up, and afterwards only problems:

| Light | Meaning |
|---|---|
| Blue, steady | Starting: loading the model, measuring exposure, start-up photo |
| Blue, blinking once a second | Motion-sensor warm-up (60 s) |
| **Three green flashes, then dark** | **Ready**; in normal operation the light is off except for photos |
| White | Taking photos during a visit |
| Red blip every 5 s | Running, but without the servo (e.g. not calibrated) |
| Red, blinking fast | Stopped by an error; the service restarts by itself 30 s later |

## Results

Measured **on the Raspberry Pi 3**:

| Metric | Value |
|---|---|
| Decision, object visible in the first photo | **≈ 2.7 s** after the trigger |
| Decision, object appears in the third photo | **≈ 5 s** |
| Decision NO (all five photos analysed) | **≈ 7.5 s** |
| Analysis per photo | 0.75–1.4 s (4 CPU cores) |
| Model start-up | about 1.5 s, once; the model then stays in memory |
| Servo stroke | 0.31–0.34 s per 85° movement; with the 0.5 s hold about 1.2 s |
| Memory | about 170 MB for recognition (of the Pi's 905 MB) |
| CPU while waiting for a crow | 0.2 % of one core |
| Network use | none: the self-test blocks every network call |

**Recognition of caps** (bench sessions, 2026-10-15; not a held-out benchmark): in good light drink caps scored a median **0.96**. The bench's round floor looked like a cap even when empty (up to 0.99); on a plain grey card, with descriptions only for things the box must reject, all 14 caps and 6 lids tested scored at least **0.81**, other objects at most **0.11** and the empty tray **0.00**, even in dim light ([RECOGNITION](docs/RECOGNITION.md)).

## Hardware

| Part | Role |
|---|---|
| Raspberry Pi 3 Model B (1 GB) | Runs everything: sensors, camera, recognition, servo |
| Raspberry Pi Camera Module V2 (IMX219) | Looks down at the tray |
| PIR motion sensor HC-SR501 on GPIO17 | Wakes the system when a crow arrives; both potentiometers at minimum, jumper on H; a short tube narrows the zone ([HARDWARE](docs/HARDWARE.md#pir-settings-owner-2026-10-14)) |
| RGB LED module on GPIO27/22/23 (white LED strip via MOSFET planned) | The intake is dark, so this is the only light the camera sees |
| JAMARA 033212 micro servo on GPIO18 (hardware PWM) | Tips the tray: centre 1500 µs, reward side 2500 µs, dump side 605 µs |
| Power: USB supply today, a power bank for autonomy | The servo should get its own supply or power-bank port ([POWER](docs/POWER.md)) |

The planned housing (food on top, intake and ledge in the middle, waste below), its mechanisms, materials and mounting options are in [MECHANICS](docs/MECHANICS.md).

## Software

| Component | What it does |
|---|---|
| `detect.py` | The production loop: PIR, light, camera, recognition of the tray area, decision, servo strokes, logging |
| `recognition.py` | Loads the ONNX model and scores a picture against the descriptions |
| `lights.py` | Camera light and status light |
| `servo_bench.py` | Hardware-PWM servo control with ramped moves, power checks and calibrated positions; also the calibration tool |
| `export_model.py` | Setup step: bakes the image encoder and the description embeddings into one 46 MB ONNX file |
| `selftest.py` | Runs the production logic on the Pi with the real camera, stored photos, optional real servo strokes, and all network access blocked |
| `report.py` | Prints the recorded visits (decision, scores, timing, stroke) |
| `deploy/` | Installer, model build script, update script, systemd service |

**Stack:** Raspberry Pi OS Lite 64-bit (Debian 13), Python 3.13, ONNX Runtime, OpenCV, gpiozero/lgpio, rpicam-apps, Linux hardware PWM, systemd.

**Design principles:**
- **Fully offline.** The Pi sits in the field isolated from any network; a computer is used only for setup.
- **Energy first.** Between visits only a light-weight wait for the motion sensor runs and the servo holds the tray; the camera and the light are off.
- **Resident model.** Loaded once at start-up and kept in memory.
- **Fail safe.** Camera, model or servo errors never cause a reward; a failed stroke is logged and the next visit tries again.
- **Restartable.** Offline the Pi has no reliable clock, so logs and photos are named by boot and sequence number; photos are pruned so the SD card cannot fill up.

## Recognition without training

A deliberate constraint was **no custom training**: the system had to work with a ready-made model on a Raspberry Pi 3.

1. **Zero-shot classification.** [MobileCLIP2-S0](https://huggingface.co/timm/MobileCLIP2-S0-OpenCLIP) compares a picture with text descriptions such as "a photo of a bottle cap", "a photo of a jar lid" or "a photo of a leaf". The cap score is the probability of the four cap and lid descriptions together.
2. **Edge deployment.** The image encoder and the precomputed description embeddings are exported into one ONNX graph, so the Pi needs neither PyTorch nor the text model: start-up drops from about **90 s to 1.5 s**, memory from **717 MB to about 170 MB**, with identical scores.
3. **Fixed tray area.** The model rates the whole picture, so only the tray floor is shown to it, set once per unit.

## Engineering challenges solved

| Problem | Finding | Solution |
|---|---|---|
| Model returned nonsense | Loading local weights made the library use the wrong image normalisation; clearly visible objects scored 0.01–0.06 | Pass the model's own preprocessing explicitly |
| 90 s start-up on the Pi | Almost all of it was fixed set-up work | Bake everything fixed into one ONNX file; keep it resident |
| 6–8 s time limit | Each photo with auto-exposure took 3.4 s | Meter exposure once, then shoot immediately: about 0.5 s per photo |
| Recognition failed at random | Room light leaking into the box changed colours and scores | Dark intake; the system's own light is the only light |
| Deposits went unnoticed | A PIR does not see cold objects | The PIR only wakes the system; the camera decides |
| The empty tray looked like a cap | A round floor inside a round tube, seen from above, scored up to 0.99 "bottle cap" | Plain grey rectangular tray, fixed tray area |
| Servo browned out the Pi | Switching the pulses off let the tray drift; the next move started with a full-speed jump | Hold the servo at the centre between moves and ramp from the held position |
| 5.5 % CPU while doing nothing | gpiozero's edge detection polled the motion sensor constantly | Read the sensor ten times a second: 0.2 % |
| No evidence after crashes | Raspberry Pi OS keeps the system log in RAM | Persistent log, capped at 50 MB |

The dated record is in [HISTORY](docs/HISTORY.md).

## Energy and autonomy

The box is meant to run for days on a power bank, later with solar charging. The idle Pi dominates the energy budget (about 1.4 W, roughly 34 Wh a day, *estimated*), so everything is off between visits. A 20 000 mAh power bank should last about 1.5 days (*estimated*). Further measures (Wi-Fi, Bluetooth and HDMI off, night shutdown, a Raspberry Pi Zero 2 W) and phone access to statistics, a feature still to be investigated, are in [POWER](docs/POWER.md).

## Install it yourself

You need: a Raspberry Pi 3 Model B, a Raspberry Pi Camera Module V2, a PIR motion sensor (HC-SR501 type), an RGB LED module, a micro servo with its own 5–6 V supply, a microSD card (8 GB is enough), and a computer for the set-up (Linux or macOS).

1. **Prepare the Pi.** Write *Raspberry Pi OS Lite (64-bit)* (Debian 13) with Raspberry Pi Imager; set a user, Wi-Fi (for set-up only) and SSH. Wire the parts as in [HARDWARE](docs/HARDWARE.md) with all power off.
2. **Install with one command** on your computer (replace `<user>` and `<pi>`):
   ```bash
   git clone https://github.com/artsensiva/crown-crows.git && cd crown-crows
   bash deploy/setup_pi.sh <user>@<pi>
   ```
   It builds the model (downloads 300 MB of weights at a pinned revision, checks them, exports the 46 MB ONNX model), copies everything to the Pi and runs the installer there: system packages, Python environment, hardware PWM, permissions, persistent log, the service, and a **self-test** on tray photos that ship with the repository, with the network blocked. The Pi asks for its password only if a system step still needs it. Reboot when it asks you to. Add `--fresh` to rebuild everything on the Pi from scratch (calibration, photos and logs stay).
3. **Set up your unit:** calibrate the servo with `servo_bench.py` ([SERVO](docs/SERVO.md#calibration-procedure)) and set the tray area ([DEPLOY](docs/DEPLOY.md)).
4. **Test from a cold start without network** ([TESTING](docs/TESTING.md)).

The author's own unit is installed exactly this way. **Updating** later is one command on your computer: `bash deploy/update_pi.sh <user>@<pi>` (calibration and data stay). Details and SD-card cloning: [DEPLOY](docs/DEPLOY.md).

## Operating it

The service starts by itself at boot and needs no network. Useful commands on the Pi:

```bash
systemctl --user status crown-crows-detect                     # is it running?
journalctl --user -u crown-crows-detect -f                      # live log
cd ~/crown-crows && .venv-detector/bin/python -B report.py      # visits since this boot
cd ~/crown-crows && .venv-detector/bin/python -B selftest.py    # self-test (stop the service first)
cd ~/crown-crows && python3 -B servo_bench.py --status          # servo state and calibration
```

Production settings are in [`deploy/crown-crows-detect.service`](deploy/crown-crows-detect.service): `--accept 0.6 --servo full --dump-seconds 0.5 --ignore-seconds 25`; per-unit settings (servo positions, tray area) are in `config/`. The runtime needs four Python packages (onnxruntime, OpenCV headless, numpy, Pillow) plus the system's GPIO libraries. Visit photos are capped at the last 1000 visits (about 1.5 GB), logs rotate at 20 MB, the system log is capped at 50 MB.

## Repository layout

```
crown-crows/
├── detect.py               production detection loop
├── recognition.py          ONNX model and the cap descriptions
├── lights.py               camera light and status light
├── servo_bench.py          servo control and calibration tool
├── export_model.py         one-time export of the model to ONNX (used by build_model.sh)
├── selftest.py             on-device self-test with the network blocked
├── report.py               table of recorded visits
├── selftest-photos/        tray photos and tray area used by the self-test
├── deploy/
│   ├── crown-crows-detect.service  systemd user service (production settings)
│   ├── install.sh                  installer for a fresh Pi
│   ├── build_model.sh              builds the model on a setup computer
│   ├── setup_pi.sh                 installs on a Pi in one command (from the setup computer)
│   ├── update_pi.sh                updates an installed Pi in one command
│   └── requirements-runtime.txt    pinned runtime packages
└── docs/                   design, measurements, history and operations
```

## Limitations and next steps

- Recognition has been tested on one bench session, not a large held-out dataset; scores are not calibrated probabilities. The threshold is confirmed on the grey tray next.
- The model does not tell a drink cap from a larger lid; the intake slot limits the size instead.
- "Any one of five photos" gives more chances, so an object that briefly looks like a cap can earn a reward; an accepted trade-off.
- The light is a weak RGB module; a white LED strip is planned ([LIGHTING](docs/LIGHTING.md)).
- The servo is powered from the Pi, which reported undervoltage; it needs its own supply ([POWER](docs/POWER.md)).
- No housing or food dispenser yet; the reference design is in [MECHANICS](docs/MECHANICS.md).
- Version 2 should train crows step by step by itself ([ROADMAP](docs/ROADMAP.md)).

## Ethics and safety

- Birds first: only objects that are safe to carry are rewarded; welfare questions (food, daily reward limit, placement) are settled with specialists before field use ([MISSION](docs/MISSION.md#3-animal-welfare)).
- Food and waste are physically separated; collected objects stay in a closed container.
- No reward is given when something fails.
- No personal data, network configuration, keys or private photos are published.

## Documentation

| File | Contents |
|---|---|
| [MISSION](docs/MISSION.md) | Mission, why caps and lids, prior work, research directions |
| [ALGORITHM](docs/ALGORITHM.md) | One visit, step by step, and why it is built this way |
| [RECOGNITION](docs/RECOGNITION.md) | Model, descriptions, export, bench results |
| [MECHANICS](docs/MECHANICS.md) | Housing design: layout, dimensions, tray and food mechanisms, sensors, materials, mounting, Berlin rules |
| [HARDWARE](docs/HARDWARE.md) | Components, pin assignments, wiring, PIR settings |
| [SERVO](docs/SERVO.md) | Servo power, hardware PWM, calibration |
| [LIGHTING](docs/LIGHTING.md) | White light upgrade |
| [POWER](docs/POWER.md) | Energy budget, power bank and solar, phone access |
| [DEPLOY](docs/DEPLOY.md) | Installing, setting up and updating a unit |
| [TESTING](docs/TESTING.md) | Test from a cold start without network |
| [OPERATIONS](docs/OPERATIONS.md) | Offline operation, reading results, shutdown |
| [ROADMAP](docs/ROADMAP.md) | Next steps, open decisions, version 2 |
| [HISTORY](docs/HISTORY.md) | Dated record of findings and decisions |

**Licence:** all rights reserved ([LICENSE](LICENSE)). This repository is published for viewing; using, building or running the system requires written permission. Private individuals can get permission free of charge; public authorities and companies under a commercial licence. Contact: artem.galukhin@gmail.com.

The MobileCLIP2 weights are not included: `build_model.sh` downloads them, and Apple's licence (`apple-amlr`) allows them, and the model exported from them, only for non-commercial research. A product for public authorities needs a recognition model under a business-friendly licence first ([ROADMAP](docs/ROADMAP.md)).
