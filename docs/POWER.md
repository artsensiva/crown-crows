# Energy and autonomy

Goal: Crown Crows runs for days on a power bank (later with solar charging), without network and without anyone looking after it. Figures marked *(est.)* come from published measurements of the same hardware and must be confirmed with a USB power meter on our unit; everything else was measured on the Pi.

## Where the energy goes

| Consumer | When | Power |
|---|---|---|
| Raspberry Pi 3 Model B, idle | always | ≈ 1.3–1.4 W (≈ 260 mA at 5 V) *(est.)* ([linuxhint](https://linuxhint.com/raspberry_pi_3_power_requirements/); [pidramble](https://pidramble.com/node/27)) |
| Recognition (3 CPU cores) | ≈ 1–5 s per visit | + ≈ 1.5 W *(est.)*; about 1.3 J per photo, so the thread count changes the daily energy by about 0.1 % ([RECOGNITION](RECOGNITION.md#thread-benchmark-100-visit-photos-2026-10-17)) |
| Tailscale (only if access from the internet is set up) | always | small CPU use (measured below), but it keeps the Wi-Fi radio active *(cost to be measured)* |
| Camera module | ≈ 0.6 s per photo, up to 3 photos per visit | + ≈ 0.25 W *(est.)* |
| Servo stroke | ≈ 1.2 s per visit | peaks up to 0.6–0.75 A (manufacturer maximum) |
| Servo holding the tray at the centre | always | small holding current *(est.: a few to a few tens of mA with a light tray)*; to be measured |
| RGB light: camera light / start-up signals | ≈ 5 s per visit / only while starting | a few mA; negligible on average |

Daily energy is dominated by the idle Pi: about 1.4 W × 24 h ≈ 34 Wh *(est.)*. Even 100 visits a day add only about 0.5 Wh. **Reducing the idle consumption is what matters.**

## Measured idle load, 2026-10-17

One minute while waiting for a crow, CPU time read from `/proc` on the Pi (no visit, dashboard closed):

| | CPU |
|---|---|
| Whole Pi | **0.5 % of the four cores**: the processor sleeps almost all the time |
| Tailscale (`tailscaled`) | 0.73 % of one core, now the largest single consumer |
| Detector waiting for a crow | 0.3 % of one core |
| Monitoring server | runs only while a dashboard page is open (each open page reads the Pi every 3 s) |

**Assessment.** The software is no longer where energy goes: the idle hardware is. About 1.3–1.4 W around the clock *(est.)* is about 34 Wh a day; even 100 visits a day add about 0.5 Wh (under 2 %). The servo's holding current is unknown and must be measured; releasing it is not an option on this unit (the tray drifts off centre). On the bench, running from the mains, energy does not matter; it matters only once the box runs on a battery. No figure in watts has been measured yet.

**Order of work for battery operation:**

1. **Measure:** a USB power meter (about 10–15 €) between supply and Pi; replace every *(est.)* figure here ([How to measure](#how-to-measure)). Without it every further choice is a guess.
2. **Night shutdown:** about 40 % less energy; needs a timer or a small microcontroller to switch the Pi on in the morning ([Bigger savings](#bigger-savings-research-options)).
3. **Wi-Fi and Tailscale off in the field:** saves the radio, but the dashboard is then not reachable from the internet. A choice between convenience and battery life.
4. **HDMI, Bluetooth and unused services off:** together about 10–15 % *(est.)*, one-time settings ([Measures that need root](#measures-that-need-root-recommended-for-field-use-not-yet-applied)).
5. **Raspberry Pi Zero 2 W:** roughly half the idle consumption *(est.)*, same software.

For reference: a 20 000 mAh power bank lasts about 1.5–1.7 days *(est.)*; weeks without recharging need night shutdown and a solar panel.

## What the additions of 2026-11-20 cost

Measured on the Pi (CPU time) and converted at about 0.5 W per busy core *(est.; no watt meter yet)*, against about 1.4 W and 34 Wh a day for the idle Pi *(est.)*:

| Addition | Measured | Energy |
|---|---|---|
| The detector's loop now also checks two files (live-photo request, pause) ten times a second | 92 µs per pass = 0.09 % of one core | about 0.5 mW, 0.011 Wh a day |
| Brightness measuring for the exposure after each photo | 2.4 ms per photo | about 1 mJ per photo, 0.0001 Wh a day at 100 visits |
| 📷 Live photo (light on about 1.7 s, one photo, a small JPEG, the sharpness number) | 0.83 CPU-seconds per press | about 0.8 J per press; 20 presses a day 0.0045 Wh |
| Dashboard open: `/api/now` now also reads three small files and the system's right to reboot (once a minute, 37 ms) | 12.7 ms per request against 12.2 ms before, plus 37 ms a minute: +0.07 % of one core | about 0.4 mW, only while a page is open |
| Pause, Restart, Reboot, food counter, threshold | no work until pressed (the counter is computed in the browser) | none |
| Exposure itself | a shorter shutter in daylight makes a photo about 0.1 s quicker (0.37 against 0.47 s) | slightly less |

**Total: about 0.016 Wh a day, under 0.05 % of the daily budget**, far below what a USB power meter resolves (1–2 %); even if the 0.5 W per core were three times too low it stays below 0.2 %. The detector's own idle CPU measured 0.55 % of one core on 2026-11-20 against about 0.3 % on 2026-10-17: the loop checks explain 0.09 of the difference, the rest is the Pi's frequency scaling (it was running throttled at the time).

For comparison, not an addition of today: Tailscale (access from the internet) uses 0.73 % of one core and keeps the Wi-Fi radio busy, more than all of the above together; recognition on 3 threads instead of 4 saves about 0.3 J per photo.

## Measures already in place (software)

| Measure | Effect (measured on the Pi, 2026-10-14) |
|---|---|
| The motion sensor is read directly ten times a second, without gpiozero's edge detection, whose helper thread in `lgpio` polled constantly | Detector CPU use while waiting: **5.5 % → 0.2 % of one core** |
| The status light signals only the start-up (three green flashes when ready) and problems; it is dark in normal operation, and its thread sleeps until the next change | included above |
| Optional: switch the servo's pulses off at the centre between visits (`--servo-idle release`) | saves the holding current, **but only usable if the tray stays at the centre without pulses**; on the first unit it drifted, causing a jump and an undervoltage at the next stroke, so it was `hold` until 2026-11-21; trial of `release` on the new prototype since then ([SERVO](SERVO.md)) |
| The camera runs only during a visit (one short `rpicam-still` call per photo); exposure is measured once at start-up, then corrected from the tray's brightness (2–3 ms per photo) | camera idle otherwise |
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

The servo stays on the Pi's 5 V pin (owner's decision); a 2200 µF / 63 V electrolytic capacitor across its + and − wires was tested and later removed. The dashboard sorts every kernel undervoltage report by what the box was doing, and the servo log records whether a dip began during a move ([MONITOR](MONITOR.md#where-the-power-dips-come-from)).

| Setting | Dips while photographing and recognising | Dips beginning during servo moves |
|---|---|---|
| 4 recognition threads | every visit (9 of 9) | not separable (the Pi was still low from recognition) |
| 2 threads | none | every tilt to the reward side (7 of 7) |
| 2 threads, slower servo ramp | none | every tilt to the reward side; none to the dump side |
| 3 threads (production), with the capacitor | none | none in 14 moves in one test, 1 in 14 in a later one |
| 3 threads, capacitor removed (8 visits) | none | 3 of 16 moves (all tilts to the dump side), plus one dip right after a return to the centre |

Conclusions: four recognition threads together with camera and light drew more than the supply could hold, and the Pi slowed its CPU; three threads avoid that and decide faster. The servo still causes short dips on some tilts, on either side from test to test; with or without the capacitor the counts stay small and vary more between tests than between the two set-ups, so the capacitor showed no clear benefit and was removed (owner, 2026-10-17). **No crash, restart or failed stroke has come from any dip**, so the dashboard shows them as notes. Still to check: the power supply's rating and cable, and whether the tray meets resistance on the reward side.

## Unexpected resets, 19-20 Nov 2026 (cause open)

Five abrupt ends of the run in about 21 hours after the box was set up on a power bank fed from the mains, two of them ending with "Undervoltage detected!"; software, watchdog, crash and SD card ruled out; the owner considers the supply fine. Details, evidence and the tests that would settle it: [HISTORY](HISTORY.md#unexpected-hard-resets-2026-11-19-to-2026-11-20-findings-cause-open). The low voltage at the Pi's board is the leading suspect for the slower recognition too (1.6 s per photo against 0.98 s on 17 Oct), not yet proven.

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

## Power bank charge level in the dashboard (2026-11-20)

**The Pi cannot read it from the power bank.** A Pi 3 powered through its micro-USB port does not talk to the bank; the Pi has no input to measure its own supply voltage (only the kernel's alarm below about 4.63 V, which also shows when the bank is nearly empty, but a bank holds 5 V until it shuts off, so there is no early warning); and the Pi 3 has no I2C fuel gauge. On the bench no USB device, power-supply entry or I2C bus exists.

Options, from the most practical:

| Option | What it gives | Notes |
|---|---|---|
| **INA226 (or INA219) current and voltage sensor on I2C**, in the 5 V line between bank and Pi | Real power in W, energy in Wh since the last charge, and with the bank's capacity entered once, an estimated charge in % and hours left at the current consumption; also replaces the USB power meter planned above | About 3–5 €, four wires to GPIO2/3, 3.3 V and ground. Choose a module with a small shunt (10 mΩ or less) so that its voltage drop stays small (2 A × 10 mΩ = 20 mV); the 0.1 Ω shunt of cheap INA219 boards would worsen the undervoltage. The estimate is ±10–15 % (the bank's real capacity is about 60–70 % of its label) and needs a "bank recharged" reset in the dashboard |
| A bank with its own display or app (Bluetooth) | The level for a person standing next to the box | Does not reach the dashboard; the protocols are model specific |
| A UPS HAT with a fuel gauge instead of a power bank | A real charge level over I2C | Replaces the bank, so a different power design |
| Dashboard alone | "No data for N minutes" when the bank is empty | Already there; says it only afterwards |

Recommended: the INA226 module, which also gives the measured watts needed for every energy estimate in this document.

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
