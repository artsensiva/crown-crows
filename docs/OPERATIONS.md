# Operations

## Standalone operation

In operation the Pi runs standalone and isolated from any network. A setup computer takes part only in setup: development, Git, and preparing and copying software, the model and configuration to the Pi. Everything that runs in operation works on the Pi alone.

- **Offline:** photos, recognition and decisions use no network. The self-test blocks every network call and fails if anything tries one.
- **The model is prepared during setup** (`deploy/build_model.sh`). It can also be rebuilt on the Pi itself with `export_model.py`, offline, in about two minutes, so a label change does not require the setup computer ([RECOGNITION](RECOGNITION.md)).
- **Start at boot:** the detector runs permanently as the systemd user service `crown-crows-detect` (lingering enabled) and restarts 30 s after a crash.
- **Status light:** blue while starting, blue blinking during the warm-up, three green flashes when ready, then dark; a red blip every 5 s when running without the servo; fast red blinking after an error.
- **Clock:** the Pi 3 has no real-time clock. Offline, time resumes from the last saved value after each power-up, so timestamps can be wrong. Logs therefore use a boot identifier and sequence numbers. If real times matter (daily reward limits, schedules), add a battery-backed RTC module, for example DS3231 on I²C.
- **Access:** with no network there is no SSH. Retrieving photos or logs and updates are maintenance steps: reconnect temporarily, or use the microSD card or a local console.
- **Updates:** avoid restarting the service while a visit is in progress; the stroke is then cut short (the tray still returns to the centre).
- **System log:** Raspberry Pi OS keeps it in RAM by default; `deploy/install.sh` makes it persistent with a 50 MB cap, so a crash leaves evidence.
- **Energy:** see [POWER](POWER.md).

## Reading the results

```bash
cd ~/crown-crows && .venv-detector/bin/python -B report.py          # visits since this boot
cd ~/crown-crows && .venv-detector/bin/python -B report.py --all-boots --last 20
journalctl --user -u crown-crows-detect -n 50 --no-pager            # the service's own log
```

Each visit has its photos in `captures/<boot>-<sequence>-<pid>/` and one line in `logs/detect.jsonl` with the decision, every photo's `cap_score`, the timings and the servo stroke.

## Setup access

During setup, with Wi-Fi and SSH configured, administer the Pi from the setup computer with a key (keys are never part of the repository):

```bash
ssh -i ~/.ssh/<key> <user>@<pi>
```

Never disable host-key checks or dismiss changed-key warnings without investigation. Keep passwords out of chat, shell commands and Git.

## Safe shutdown

```bash
sudo poweroff
```

Wait for the shutdown to finish (30–60 s, until the green activity LED stops), then unplug the Pi and the servo supply. Change cables, CSI and GPIO wiring only with all power removed.

## Power check

```bash
vcgencmd get_throttled
```

`0x0` means no limiting since boot. Any active undervoltage must be fixed before unattended operation ([POWER](POWER.md)).
