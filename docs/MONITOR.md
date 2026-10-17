# Monitoring dashboard

A plain web page for a phone or computer on the same network as the Pi: what the box is doing right now, summary, live device readings, visits per day, recent visits with their photos, servo undervoltage readings, errors from the system log, and CSV/JSON export.

## Open it

`deploy/install.sh` prints the address at the end, for example `http://<pi-address>:8080/#token=<token>`. Open it once; the browser remembers the token. The token is in `config/local.monitor.json` on the Pi (created once by the installer; delete the file and re-run the installer to get a new one).

## How it works

- **Nothing runs while nobody is looking.** systemd listens on port 8080 (`deploy/crown-crows-monitor.socket`) and starts `monitor/server.py` only when a browser connects; the server exits after 2 minutes without requests.
- **Read-only.** The server serves only the page, the two logs (`logs/detect.jsonl`, `logs/servo.jsonl`, and their `.1` generations) from a byte position on, single photos from `captures/`, live readings (at most every 10 s) and the last warnings from the system log. No hardware control, no writes. Standard library only; lowest CPU and disk priority (`Nice=19`, idle I/O, `CPUQuota=20%`, `MemoryMax=64M`).
- **"Now", every 3 s while the page is open:** the state (starting, ready, visit in progress, triggers ignored for N s, detector stopped), motion sensor level, light, servo position, last visit, CPU load. It comes from cheap reads only: one `pinctrl` call for the GPIO levels, the PWM duty cycle, the end of the visit log, `/proc`; the detector's start time at most once a minute. Measured on the Pi: about 8 ms of CPU per reading, about 0.3 % of one core while the page is open. When a new visit appears, its record is fetched at once.
- **The browser does the work.** It loads the logs once, then fetches only new lines: every 5 s, slowing to 30 s while nothing happens, and not at all while the page is in the background. Statistics and exports are computed in the browser.
- **Access:** local network only, with the token. The connection is plain HTTP, so use it on a trusted network (WPA2 Wi-Fi).

## What the numbers mean

| Field | Meaning |
|---|---|
| State | Derived: detector start time, light (white = photos being taken), the 25 s after the last trigger |
| Motion sensor, light, servo | Read directly: GPIO17 level; GPIO27/22/23 levels (active-low); PWM pulse compared with the calibrated positions |
| YES / NO | The software's decision for a visit |
| Reward commands | Servo stroke to the reward side completed; food delivery is not measured |
| Best score | Highest `cap_score` of the visit's photos: a model similarity score, not a calibrated probability |
| Decision time | From the PIR trigger to the decision |
| Analysis per photo | Recognition time per photo on the Pi |
| Times, dates | The Pi's clock: correct while it is synchronised over the network, unverified offline (no real-time clock) |
| Device (live) | Read when the page asks: service state, restarts, uptime, clock sync, throttling flags, temperature, CPU clock, memory, disk |
| Undervoltage | Servo moves during which the Pi reported undervoltage (`logs/servo.jsonl`), and kernel undervoltage events (system log) |
| Power draw, battery, solar | Not measured: needs instrumentation |

History lasts as long as the logs and photos are kept: photos for the last 1000 visits; each log up to two 20 MB generations (at about 0.7 KB per visit, tens of thousands of visits); the system log up to 50 MB.
