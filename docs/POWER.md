# Energy and autonomy

Goal: Crown Crows runs for days on a power bank (later with solar charging), without network and without anyone looking after it. Figures marked *(est.)* come from published measurements of the same hardware and must be confirmed with a USB power meter on our unit; everything else was measured on the Pi.

## Where the energy goes

| Consumer | When | Power |
|---|---|---|
| Raspberry Pi 3 Model B, idle | always | ≈ 1.3–1.4 W (≈ 260 mA at 5 V) *(est.)* ([linuxhint](https://linuxhint.com/raspberry_pi_3_power_requirements/); [pidramble](https://pidramble.com/node/27)) |
| Recognition (4 CPU cores) | ≈ 1–6 s per visit | + ≈ 1–2 W *(est.)* |
| Camera module | ≈ 0.6 s per photo, up to 5 photos per visit | + ≈ 0.25 W *(est.)* |
| Servo stroke | ≈ 1.2 s per visit | peaks up to 0.6–0.75 A (manufacturer maximum) |
| Servo holding the tray at the centre | always | small holding current *(est.: a few to a few tens of mA with a light tray)*; to be measured |
| RGB light: camera light / start-up signals | ≈ 5 s per visit / only while starting | a few mA; negligible on average |

Daily energy is dominated by the idle Pi: about 1.4 W × 24 h ≈ 34 Wh *(est.)*. Even 100 visits a day add only about 0.5 Wh. **Reducing the idle consumption is what matters.**

## Measures already in place (software)

| Measure | Effect (measured on the Pi, 2026-10-14) |
|---|---|
| The motion sensor is read directly ten times a second, without gpiozero's edge detection, whose helper thread in `lgpio` polled constantly | Detector CPU use while waiting: **5.5 % → 0.2 % of one core** |
| The status light signals only the start-up (three green flashes when ready) and problems; it is dark in normal operation, and its thread sleeps until the next change | included above |
| Optional: switch the servo's pulses off at the centre between visits (`--servo-idle release`) | saves the holding current, **but only usable if the tray stays at the centre without pulses**; on the first unit it drifted, causing a jump and an undervoltage at the next stroke, so the default is `hold` |
| The camera runs only during a visit (one short `rpicam-still` call per photo); exposure is measured once at start-up | camera idle otherwise |
| The light is off except for photos and brief status blips | |
| The model stays in memory; nothing is loaded or downloaded per visit; no network use at all | no Wi-Fi traffic needed |
| Logs rotate at 20 MB, photos are capped at 1000 visits (≈ 1.5 GB) | no unbounded SD-card writes |

## Measures that need root (recommended for field use, not yet applied)

Apply on the Pi and test each one; some make local access harder.

| Measure | Saving *(est.)* | How |
|---|---|---|
| Wi-Fi off in the field | ≈ 10+ mA, plus no radio activity ([Pi Supply](https://learn.pi-supply.com/make/how-to-save-power-on-your-raspberry-pi)) | `sudo nmcli radio wifi off` (survives reboots; to undo you need a keyboard and monitor: `sudo nmcli radio wifi on`) |
| Bluetooth off (unless used for phone access, below) | a few mA | add `dtoverlay=disable-bt` to `/boot/firmware/config.txt`, then `sudo systemctl disable --now bluetooth` |
| HDMI output off | ≈ 20–30 mA ([Core Electronics](https://core-electronics.com.au/tutorials/disable-features-raspberry-pi.html)) | method depends on the display driver on Debian 13; to be tested |
| Activity LED off | ≈ 5 mA ([Pi Supply](https://learn.pi-supply.com/make/how-to-save-power-on-your-raspberry-pi)) | `dtparam=act_led_trigger=none` plus the model-specific `act_led_activelow` setting from the Raspberry Pi documentation, in `config.txt`; keep the red power LED, it shows undervoltage |
| Unused services | small | `sudo systemctl disable --now avahi-daemon` |

## Measurements 2026-10-17

The servo stays on the Pi's 5 V pin (owner's decision); a 2200 µF / 63 V electrolytic capacitor was fitted across its + and − wires. The dashboard sorts every kernel undervoltage report by what the box was doing, and the servo log records whether a dip began during a move ([MONITOR](MONITOR.md#where-the-power-dips-come-from)).

| Setting | Dips while photographing and recognising | Dips beginning during servo moves |
|---|---|---|
| 4 recognition threads | every visit (9 of 9) | not separable (the Pi was still low from recognition) |
| 2 threads | none | every tilt to the reward side (7 of 7) |
| 2 threads, slower servo ramp | none | every tilt to the reward side; none to the dump side |
| 3 threads (production) | none | none in 14 moves (unexplained; to be watched) |

Conclusions: four recognition threads together with camera and light drew more than the supply could hold, and the Pi slowed its CPU; three threads avoid that and decide faster. The servo still causes short dips on the reward side; the capacitor did not remove them. **No crash, restart or failed stroke has come from any dip**, so the dashboard shows them as notes. Still to check: the power supply's rating and cable, and whether the tray meets resistance on the reward side.

## Power bank: what to look for

- **Output 5.1 V and at least 2.4–2.5 A** on the port that feeds the Pi, with a short, thick cable. The Pi 3 has already reported undervoltage with weaker power.
- **For a power-bank build, do not power the servo from the Pi's 5 V pin** (the bench box keeps it there by the owner's decision; see the measurements above). On 2026-10-14 the servo was powered from the Pi again, and the kernel logged undervoltage during strokes. Feed the servo from a **second port of the power bank** or a separate 5–6 V regulator, join the grounds, and add a 470–1000 µF capacitor across the servo supply. This keeps the Pi stable when the servo starts.
- **Auto-off.** Many power banks switch off below 50–200 mA ([voussoir](https://voussoir.net/writing/auto_off_power_banks); [0110.be](https://0110.be/posts/Powering_low_current_electronics_projects_with_power_banks)). The Pi draws more than that, but prefer a bank with an "always-on" or low-current mode.
- **Pass-through charging** if a solar panel will charge the bank while it powers the box.

## Runtime estimates

| Battery | Usable at 5 V *(est.)* | Runtime at ≈ 1.5 W average *(est.)* |
|---|---|---|
| 10 000 mAh power bank (37 Wh) | ≈ 28–30 Wh | ≈ 19–20 h |
| 20 000 mAh power bank (74 Wh) | ≈ 55–60 Wh | ≈ 1.5–1.7 days |
| 50 000 mAh power bank (185 Wh) | ≈ 140–150 Wh | ≈ 4 days |

For continuous operation, a solar panel must cover about 36 Wh per day plus losses. At northern latitudes in winter there may be only about 1.5 full-sun hours a day, which calls for a panel of roughly 60 W and a battery for a few cloudy days ([sizing example](https://www.aguilmard.com/tutorials/solar-powered-weather-station-battery-panel-sizing-2026/); [SwitchDoc](https://www.switchdoc.com/2018/02/solar-power-raspberry-pi/)).

## Bigger savings (research options)

- **Night shutdown.** Crows are active by day. Switching the Pi off at night would save about 40 % of the energy. It needs something to switch it back on in the morning (a timer or a small microcontroller), because the Pi 3 has no real-time clock or sleep mode.
- **Raspberry Pi Zero 2 W.** Same type of processor (four Cortex-A53 cores), 512 MB of memory (the detector uses about 170 MB), smaller and with tuning able to idle lower than a Pi 3 ([cnx-software](https://www.cnx-software.com/2021/12/09/raspberry-pi-zero-2-w-power-consumption/); [lo-tech](https://lo-tech.co.uk/wiki/Tuning_the_RaspberryPi_Zero2W_for_Minimum_Power_Consumption)). The software would run unchanged; recognition speed must be re-measured.
- **Faster recognition** (a small trained model, see [MISSION](MISSION.md#1-recognition)) shortens the high-power part of each visit.
- **Wake on motion.** A microcontroller watching the PIR could keep the Pi off between visits, but the Pi needs about 30 s to boot, far beyond the time a crow waits, so this only fits a different design.

## Phone access to statistics (feature to investigate)

Requirement: read statistics (visits, YES/NO, recent photos) on a phone near the box, without draining the battery.

| Option | Power | Notes |
|---|---|---|
| **Bluetooth Low Energy, read-only** | low; the radio is idle most of the time | A small GATT service on the Pi publishes counters (visits today, YES/NO, last decision); any BLE app (e.g. nRF Connect) can read them. Python libraries exist ([bless](https://pypi.org/project/bless/), [example](https://github.com/Douglas6/cputemp)). |
| **Wi-Fi hotspot on demand** | high while on | A button, or a special motion pattern, switches on a hotspot for about 10 minutes to download photos and logs, then switches it off again. |
| **Wi-Fi client, always on** | high | Not suitable for battery operation. |

Starting point for the investigation: BLE for the counters, and a short on-demand hotspot only when photos are needed. Nothing is implemented; any solution must keep the detector itself unchanged and offline, and its energy cost must be measured first.

## How to measure

Put a USB power meter between the power bank and the Pi, then record: idle and ready (light dark), a visit (photos and analysis), a servo stroke, and the effect of each root measure above. Replace the *(est.)* values in this document with the measured ones.
