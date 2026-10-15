# Installing Crown Crows on a Raspberry Pi

The complete engine runs on the Pi itself and needs no network in operation. Network access is only needed during installation (package downloads, copying files). Every unit, including the developer's, is installed the same way.

## What the engine consists of

| Part | Location on the Pi | In Git? |
|---|---|---|
| Programs: `detect.py`, `recognition.py`, `lights.py`, `servo_bench.py`, `selftest.py`, `report.py` | `~/crown-crows/` | yes |
| Service definition, installer, runtime requirements | `~/crown-crows/deploy/` | yes |
| Recognition model `model.onnx` (46 MB) | `~/crown-crows/models/mobileclip2-s0/` | no: build it with `deploy/build_model.sh` on a setup computer (downloads pinned weights and exports them), or copy it from an existing unit |
| Self-test photos and their tray area (`tray.json`) | `~/crown-crows/selftest-photos/` | yes: shipped with the repository, so the self-test works on every unit without taking photos |
| Python environment with onnxruntime, OpenCV, numpy, Pillow | `~/crown-crows/.venv-detector/` | no: created by the installer |
| Servo calibration (home, dump_only, dump_reward) | `~/crown-crows/config/local.servo.json` | no: per unit, see step 6 |
| Tray area of this unit | `~/crown-crows/config/local.tray.json` | no: per unit, see step 6 |
| System settings: hardware PWM (`dtoverlay=pwm,pin=18,func=2`), lingering, persistent log | `/boot/firmware/config.txt`, systemd | set by the installer |

Production settings live in `deploy/crown-crows-detect.service`: `--accept 0.7 --servo full --dump-seconds 0.5 --ignore-seconds 25`. Per-unit settings (servo positions, tray area) live in `config/`, which updates never touch. The service file uses `%h` (the user's home folder), so any user name works as long as the project is in `~/crown-crows`.

## Fresh installation

1. **Operating system.** With Raspberry Pi Imager write *Raspberry Pi OS Lite (64-bit)*, Debian 13 "Trixie". In the Imager settings set a user name, the Wi-Fi (for setup only), SSH with a public key, and a unique host name (e.g. `crown-crows-2`).
2. **Hardware.** With all power off, connect as described in [HARDWARE](HARDWARE.md): camera to the CSI connector; PIR OUT to GPIO17 (physical pin 11), VCC to 5 V, GND to GND; light to GPIO27/22/23 (pins 13/15/16; see [LIGHTING](LIGHTING.md)); servo signal to GPIO18 (pin 12), servo + to its own 5–6 V supply, servo − to that supply **and** a Pi GND pin.
3. **Copy the project** from the setup computer (replace `<user>` and `<pi>`):
   ```bash
   git clone https://github.com/artsensiva/crown-crows.git
   cd crown-crows && bash deploy/build_model.sh
   rsync -a --exclude .git --exclude '.venv*' --exclude captures --exclude logs --exclude config \
         ./ <user>@<pi>:crown-crows/
   ```
   `build_model.sh` creates `models/mobileclip2-s0/model.onnx`. The model can also be rebuilt on the Pi itself with `export_model.py` ([RECOGNITION](RECOGNITION.md)); with another PyTorch version its checksum differs, but the scores are identical.
4. **Install** on the new Pi (asks for the user's password; downloads about 100 MB):
   ```bash
   cd ~/crown-crows && bash deploy/install.sh
   ```
   It checks the files and the model checksum, installs `rpicam-apps-lite`, `python3-venv`, `python3-gpiozero` and `python3-lgpio`, builds `.venv-detector` from `deploy/requirements-runtime.txt`, enables hardware PWM, adds the user to the `gpio` and `video` groups, makes the system log persistent (Raspberry Pi OS keeps it in RAM by default; capped at 50 MB), enables lingering, installs the service and runs the self-test. It can be run again safely. If your model checksum differs, put it into `--model-sha256` in the service file and into `install.sh`.
5. **Reboot** (`sudo reboot`) so hardware PWM and the group changes take effect. The service starts by itself (status light: blue, then blue blinking, then three green flashes when ready, then dark). Without a servo calibration it detects but makes no strokes, shows a red blip every 5 s, and says so in its log.
6. **Set up this unit** (mechanism clear, servo supply on):
   - **Servo:** follow [SERVO](SERVO.md#calibration-procedure) with `servo_bench.py` and save `home`, `dump_only` and `dump_reward`. If the mechanism is identical to an existing unit, start from its `config/local.servo.json` and check each position with `python3 -B servo_bench.py --goto <position> --clear`.
   - **Tray area:** each start saves a photo of the empty tray in `captures/<boot>-0000-<pid>/image-01.jpg`. Read on it where the tray floor is, as fractions of the photo width and height (left, top, right, bottom), and save them in `config/local.tray.json`, for example `{"tray": [0.27, 0.02, 0.74, 0.66]}`. Only the tray floor should be inside the area: no walls or rims. Without the file the whole photo is analysed.
   - Apply: `systemctl --user restart crown-crows-detect`.
7. **Self-test on the Pi.** `install.sh` already runs it once without the servo. After calibration run it again, also with real strokes (stop the service first; the network is blocked inside the test):
   ```bash
   systemctl --user stop crown-crows-detect
   cd ~/crown-crows && .venv-detector/bin/python -B selftest.py                   # decisions and timing
   cd ~/crown-crows && .venv-detector/bin/python -B selftest.py --servo --clear   # plus real strokes
   systemctl --user start crown-crows-detect
   ```
   Expected: `RESULT: all scenarios correct`.
8. **Offline test from a cold start**: [TESTING](TESTING.md).

## Cloning an SD card (identical units)

1. On the working Pi: `sudo poweroff`, wait until the green LED stops, unplug, take out the card.
2. On the setup computer copy the whole card to an image file and write it to a new card of the same or larger size (Raspberry Pi Imager "Use custom", or `dd`).
3. Boot the second Pi with the network available and make the copy its own machine:
   ```bash
   sudo hostnamectl set-hostname crown-crows-2
   sudo rm /etc/machine-id && sudo systemd-machine-id-setup
   sudo rm /etc/ssh/ssh_host_* && sudo dpkg-reconfigure openssh-server
   ```
4. Continue with step 6 above: this unit's servo and tray area, then the self-test.

## Updating an installed Pi

One command on the setup computer, in a clone of the repository (no password; calibration, photos, logs, model and Python environment stay):

```bash
bash deploy/update_pi.sh <user>@<pi>
```

It pulls the latest version from GitHub, copies it to the Pi, installs the service file, runs the self-test and restarts the service. If `deploy/install.sh`, the runtime requirements or the model changed, run `bash deploy/install.sh` on the Pi afterwards. With a special SSH key, pass it in `SSH_OPTS`, e.g. `SSH_OPTS="-i ~/.ssh/id_ed25519" bash deploy/update_pi.sh <user>@<pi>`.

## Storage needed

Raspberry Pi OS Lite with the system packages about 2.7 GB, Crown Crows (environment, model, self-test photos) about 0.35 GB, visit photos capped at about 1.5 GB (1000 visits), system log capped at 50 MB: at most about 4.6 GB, so an **8 GB card is enough** (use an A1-rated card or better). On smaller cards lower `--keep-batches` in the service file.
