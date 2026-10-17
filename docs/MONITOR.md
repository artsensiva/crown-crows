# Monitoring dashboard

A plain web page for a phone or computer on the same network as the Pi: what the box is doing right now, summary, live device readings, visits per day, recent visits with their photos, servo undervoltage readings, errors from the system log, and CSV/JSON export.

## Open it

`deploy/install.sh` prints the address at the end, for example `http://<pi-address>:8080/#token=<token>`. Open it once; the browser remembers the token. The token is in `config/local.monitor.json` on the Pi (created once by the installer; delete the file and re-run the installer to get a new one).

## How it works

- **Nothing runs while nobody is looking.** systemd listens on port 8080 (`deploy/crown-crows-monitor.socket`) and starts `monitor/server.py` only when a browser connects; the server exits after 2 minutes without requests.
- **Read-only.** The server serves only the page, the two logs (`logs/detect.jsonl`, `logs/servo.jsonl`, and their `.1` generations) from a byte position on, single photos from `captures/`, live readings (at most every 10 s) and the last warnings from the system log. No hardware control, no writes. Standard library only; lowest CPU and disk priority (`Nice=19`, idle I/O, `CPUQuota=20%`, `MemoryMax=64M`).
- **"Now", every 3 s while the page is open:** the state (starting, ready, visit in progress, triggers ignored for N s, detector stopped), motion sensor level, light, servo position, last visit, CPU load, CPU clock and temperature, memory and disk. It comes from cheap reads only: one `pinctrl` call for the GPIO levels, the PWM duty cycle, the end of the visit log, `/proc` and `/sys` files (no external programs for clock, temperature, memory and disk); the detector's start time at most once a minute. Measured on the Pi: about 8 ms of CPU per reading, about 0.3 % of one core while the page is open. When a new visit appears, its record is fetched at once.
- **The browser does the work.** It loads the logs once, then fetches only new lines: every 5 s, slowing to 30 s while nothing happens, and not at all while the page is in the background. Statistics and exports are computed in the browser.
- **Access:** local network only, with the token. The connection is plain HTTP, so use it on a trusted network (WPA2 Wi-Fi).

## Two modes

- **🐦 Crow mode** (default): a friendly view. The mood card answers first **"Is the box working?"**, then lists each point with an urgency tag (🚨 urgent, 🛠️ fix soon, ℹ️ just so you know), the numbers behind it (for power dips: how many since the Pi started and what the box was doing at each, from the kernel log read at most every 10 minutes) and a one-line fix. A big mood emoji (😎 all chill, 😬 things to look at, 😱 a problem), bubbles for what is happening right now (waiting for a crow, crow visit, snack break, tray position, temperature), today's tiles (caps, not caps, snacks served, typical decision time, caps all time), the last guest with a photo button, and each problem in one plain sentence with a one-line fix and **🤓 Nerd details** to open the full explanation.
- **Visit celebration:** when a new decision arrives while the page is open (within 3 minutes of the visit), the background bursts: 🌸🍓🍄 flowers, fruit and mushrooms for YES, 💩 for NO. Visits loaded with the page or caught up after the tab was hidden do not burst. Click the big mood emoji to preview it. Switched off when the system asks for reduced motion.
- **Links to the details:** every Crow-mode figure is a link (🔎). A click opens Nerd mode at the matching table and highlights it: bubbles → Now; caps tiles → per day; not caps and the last guest → recent visits; snacks and decision time → summary; power points → Errors and power (with the system-log dips loaded). A **🐦 Back to Crow mode** button, or the browser's Back button, then returns to the friendly view where you left it.
- **Motion sensor readiness** (both modes, next to the switch): 🟢 *Ready for a crow* (the next motion starts a visit); 🟡 *Almost ready* (the detector re-arms only after the PIR has seen no movement once); ⏳ *Short pause* with a countdown bar (the 25 s window after a visit); 🔥 *Warming up* after a start; 📸 *Busy* during a visit; 🔴 *Not armed* when the detector is not running. It comes from the 3-second reading (`trigger` in `/api/now`) and counts down every second in between.
- **🔍 Last checks** (both modes, under the switch): the three latest visits, newest first, as small cards: a thumbnail of the photo that scored highest, cropped in the browser to the tray area; 👑 YES or 🙅 NO, 🥜 when a reward was given, ⚠️ when the stroke failed; how long ago; the model's best guess; the cap score against the threshold; photos taken and the decision time. One card per registered object (visit); the numbered buttons open every photo of that visit (the best one is outlined; a dot marks a photo not analysed because the decision was already made). **🔎 more about this visit** (open by default in Nerd mode, closed in Crow mode): exact time and the gap to the visit before; why the decision was made (which photo reached the threshold, or the best score when none did); time from motion to decision and how many photos were analysed; a per-photo table (taken at, what the model saw, cap score, analysis time); the servo stroke with its outcome and the low-power readings recorded during it; whether a reward was released. A click on the thumbnail opens the full best photo; *all visits →* opens the visits table. A new check is outlined briefly. Each photo is fetched once per page load (about 0.4 MB); photos already pruned on the Pi show *photo not kept*.
- **Problems in the header** (both modes, under the data time): each open problem as a small chip in a few words, most urgent first (for example *⚡ servo pulls power*, *🧠 power dips since start*); hidden when there is none. A click scrolls to the mood card (Crow mode) or to the problem list (Nerd mode).
- **Switch:** the large two-part control under the header (🐦 Crow mode | 🤓 Nerd mode); the active half is filled. The browser remembers the choice.
- **In both modes:** a dim, slowly shimmering rainbow background, and a cute bear in a black doublet and ruff silently performing Hamlet with Yorick's skull (a new line every 5 s). All of it runs in the browser only and stops with "reduce motion".
- **🤓 Nerd mode:** all the technical data, still friendly: emoji on every section and row, 😎/😬/😱 in the status bar, 👑 YES / 🙅 NO, a 🏆 on the best day. 

Both modes show the same data; the friendly one only words it differently. "Snacks served" counts reward commands sent to the servo, not food actually delivered.

## Signals at a glance

Colours always come with text, so nothing depends on colour alone.

| Signal | Meaning |
|---|---|
| Status bar: green "All systems normal" | Nothing below applies |
| Status bar: amber "Attention" | Undervoltage since boot or during recent servo moves; clock not synchronised; CPU 70 °C or more; disk under 15 % free; under 100 MB memory available |
| Status bar: red "Problem" | No connection to the Pi; detector not running; undervoltage lasting 30 s or more (read live every 3 s from the kernel's voltage monitor; a shorter dip, such as one during a servo stroke, is a warning); servo failure in the last 20 visits; CPU 80 °C or more; disk under 5 % free |
| Browser tab icon | A crow wearing a gold crown, with a dot in the status bar's colour (green, amber, red), so the state is visible from the tab alone; built into the page, no extra request |
| "LIVE · updated N s ago" next to "Now" | Counts up every second in the browser; the dot pulses at each reading from the Pi (every 3 s). Green under 10 s, amber under 60 s, red otherwise. A value that changed since the previous reading is highlighted for a moment |
| Dot next to "Data as of" | Live data under 10 s old (green), under 60 s (amber), older (red) |
| "Now" dots | Green: ready, servo at the centre. Blue, blinking: visit in progress, light on for photos, servo on its way. Amber, blinking: motion sensor HIGH. Amber: triggers being ignored after a visit. Red: detector not running |
| Visit rows | YES/NO marker; score bar with the threshold as a black line (green bar = YES); a new visit is highlighted for 3 s; decision time over 8 s in amber; servo failure in red |
| Per day | Bar for the YES rate |

The status bar is computed in the browser from data the page already has; nothing extra is read on the Pi. Below the bar, every warning opens into an explanation: what it means, why it matters, the likely cause on this box, what to do step by step, and the data behind it (for example how many of the recent servo moves had undervoltage, and when the last one was).

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
| Device (every 30 s or more) | Readings that need external programs: service state and restarts, uptime, clock sync, throttling and undervoltage flags (`vcgencmd`) |
| Undervoltage | Servo moves during which the Pi reported undervoltage (`logs/servo.jsonl`), and kernel undervoltage events (system log) |
| Power draw, battery, solar | Not measured: needs instrumentation |

History lasts as long as the logs and photos are kept: photos for the last 1000 visits; each log up to two 20 MB generations (at about 0.7 KB per visit, tens of thousands of visits); the system log up to 50 MB.

## Access from the internet (password, Tailscale Funnel)

Free, no domain and no router changes: [Tailscale Funnel](https://tailscale.com/kb/1223/funnel) gives the Pi a fixed HTTPS address such as `https://crown-crows.<tailnet>.ts.net` and forwards it to the dashboard. Anyone with the address and the password can open it.

1. **Password** (on the Pi; typed there, only a salted PBKDF2 hash is stored in `config/local.monitor.json`):
   `~/crown-crows/.venv-detector/bin/python ~/crown-crows/monitor/server.py --set-password`
   At least 10 characters. Takes effect when the monitoring server next starts (after 2 minutes without use).
2. **Tailscale** (on the Pi, needs sudo):
   `curl -fsSL https://tailscale.com/install.sh | sh`, then `sudo tailscale up --hostname crown-crows` and open the login link it prints.
3. **Funnel**: `sudo tailscale funnel --bg 8080`. The first time it prints a link to allow HTTPS and Funnel for this device in the Tailscale admin console; then run the command again. It prints the public address. `sudo tailscale funnel reset` switches it off.

**Sign-in:** the page shows a password form; the server answers a correct password with the access token, which the browser keeps if *Remember on this device* is ticked. The LAN link with `#token=…` keeps working. Five wrong passwords lock the login for 1 minute, doubling with every further wrong one up to 1 hour (kept in `config/local.monitor-lock.json`; deleting it lifts the lock). A stranger guessing can therefore also lock out real users for a while; that is accepted for a small project. To shut everyone out at once, set a new password and replace the token (signed-in browsers keep the old one until then):
`cd ~/crown-crows && python3 -c 'import json, secrets, pathlib; p = pathlib.Path("config/local.monitor.json"); s = json.loads(p.read_text()); s["token"] = secrets.token_urlsafe(18); p.write_text(json.dumps(s, indent=2))'`

**Privacy and load:** the page and API carry `noindex` so search engines do not list them. Everyone with the password can see the photos; the camera looks at the tray, but a hand may appear in a photo. Tailscale itself uses about 30–40 MB of memory; the dashboard server still only runs while someone has the page open.

## Power off button

**⏻ Power off** in the header (both modes) shuts the Pi down cleanly, for example before work on the wiring. It asks for confirmation (and warns if a visit is in progress), then shows what to do: wait until the green light stops blinking (about 20 s), then unplug. The page notices when the Pi stops answering. It cannot switch the Pi on again: plug the power back in, and the detector and the dashboard start by themselves.

This is the dashboard's only action besides reading. `POST /api/poweroff` needs the access token and the word `poweroff`, and works only with the polkit rule `deploy/50-crown-crows-poweroff.rules`, which lets this one user power off without a password and allows nothing else. `deploy/install.sh` installs it (one sudo prompt); without it the button reports "not allowed".
