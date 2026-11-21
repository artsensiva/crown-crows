# History

A dated record of what was tried, measured and decided. Detailed measurements live in [RECOGNITION](RECOGNITION.md), [ALGORITHM](ALGORITHM.md), [SERVO](SERVO.md) and [POWER](POWER.md).

## Engineering lessons carried over from the first prototype (2026-10-13 to 2026-10-15)

The hardware, the software architecture and these lessons come from the first bench prototype, built before the change of course described below.

| Lesson | What happened | Solution |
|---|---|---|
| Ready-made object detectors were not good enough | Downloaded detectors missed small objects lying in the tray | Zero-shot MobileCLIP2-S0: rates the picture against text descriptions, no training ([RECOGNITION](RECOGNITION.md)) |
| Preprocessing is critical | Loaded from a local file, open_clip silently used the wrong image normalisation; clearly visible objects scored 0.01–0.06 | Preprocessing set explicitly in the export and on the Pi |
| Start-up was far too slow | PyTorch needed about 90 s to load the model on the Pi 3 | One ONNX file with the descriptions built in: ready in about 1.5 s, stays in memory |
| Decision time | Owner requirement: a decision within 6, later 8 s | Pipelined photos and analysis: YES in 2.7–5 s, NO in about 7.5 s |
| A PIR does not see cold objects | Six objects tossed into the intake: zero PIR pulses | PIR only wakes the system; the camera decides |
| Room light changes scores | Light reaching the tray changed a score from 0.94 to 0.08 | Dark intake; the box's own light only |
| Dim light | The external LED resistors were removed for a brighter light | A brighter white light is planned ([LIGHTING](LIGHTING.md)) |
| Servo jitter and jumps | Software PWM jitters under load; switching the servo's pulses off between visits let the tray drift, and the next stroke started with a full-speed jump and undervoltage | Hardware PWM; the servo holds the centre between visits ([SERVO](SERVO.md)) |
| Idle CPU 5.5 % | gpiozero's edge detection polled constantly | The PIR level is read ten times a second: 0.2 % of one core |
| Crashes left no evidence | Raspberry Pi OS keeps the system log in RAM | The installer makes the log persistent (50 MB cap) |
| Every unit must be installed the same way | — | `deploy/install.sh` with a self-test on shipped photos; `deploy/update_pi.sh` for updates |
| PIR range | Both potentiometers at minimum, jumper on H: about 50 cm for a quick hand movement | A short tube or shroud narrows the zone further ([HARDWARE](HARDWARE.md)) |
| The analysed area matters | The model rates the whole picture: a clearly visible object scored 0.02 on a whole photo with other things in view, and 0.99 on a crop of the tray | Analyse only the tray area |

## 2026-10-15: Birds first, a change of course

An earlier version of this device was built around a kind of litter that, we later realised, could harm the birds carrying it. We had focused on the technology and underestimated the risk to the birds. That was a significant mistake. We withdrew the design and rebuilt the project around objects that are safe for crows: **bottle caps and lids** (steel crown caps, plastic drink caps, jar and container lids up to a size set by the intake slot). They are not toxic and too large to swallow ([MISSION](MISSION.md#birds-first-why-the-project-changed-course)).

The project was renamed **Crown Crows**: the crown cap, and crowning the crows for a good deed. The name check found no conflicting trademark in TMview and free domains.

## 2026-10-15: Mechanics design study

Reference design for the housing: food on top, electronics, intake chamber with tray, waste bin at the bottom; ledge, slot, food window, sensors, materials, weather, stability, mounting (pole, litter bin, wall, tilting mast) and Berlin rules ([MECHANICS](MECHANICS.md)).

## 2026-10-15: First bench session with caps

91 rounds of three photos in the bench intake (round wooden floor seen down a round tube): 32 drink caps, 12 larger lids, 37 empty trays ([RECOGNITION](RECOGNITION.md)).

- Caps scored a median 0.96 with "bottle cap", "plastic bottle cap" and "metal bottle cap"; 93 % reached 0.7.
- The empty round tray itself looked like a cap: up to 0.99.
- The model does not distinguish drink caps from larger lids.

Owner decisions:
- caps **and lids** up to a size set by the intake slot (for example 60 mm), no size rule in software;
- a **square or rectangular plain grey tray**;
- a **fixed tray area per unit** instead of searching for a round floor;
- no reference photo per visit;
- no model download, training or image collection for now;
- coins, washers or buttons need not be rejected.

## 2026-10-15: Grey-card session

A plain grey card as the tray floor, in dim light (worst case): the empty card scored 0.001, other objects at most 0.057, caps and lids mostly high but some low in the dim light ([RECOGNITION](RECOGNITION.md#grey-card-session-2026-10-15-dim-light-worst-case)). Owner decisions: "jar lid" joins the cap descriptions; the self-test photos come from this session. The threshold waits for better light.

## 2026-10-15: Second grey-card session, descriptions and threshold

Light leaks sealed, white reflectors added (colours neutral, still dim). With coin, button and washer listed as competitors, "button" took most of the vote from caps seen from above. Without them, all 14 caps and 6 lids of both sessions scored at least 0.81, other objects at most 0.11. Owner decisions: these three descriptions removed (a coin is now rewarded, which is acceptable), threshold 0.6 ([RECOGNITION](RECOGNITION.md#second-grey-card-session-2026-10-15-leaks-sealed-reflectors-still-dim)).

## 2026-10-15: The bench Pi runs Crown Crows; one-command installation

- The owner's Pi was switched from the first prototype's installation to Crown Crows; its servo calibration carried over, and the old data was backed up to the setup computer and removed from the Pi.
- The installer now checks every system step first and asks for the password only when something is missing.
- Analysing the whole tray area at full resolution made a NO take 10 s; the area is now reduced to at most 512 px before recognition (same scores): YES 2.6–2.7 s, NO 6.6–6.9 s on the Pi.
- A fresh clone failed to build the model (torchvision did not match the pinned torch); with torch and torchvision both from the CPU index and pinned versions, a fresh clone builds a byte-identical model.
- **Verified by the owner:** `bash deploy/setup_pi.sh <user>@<pi> --fresh` from a fresh GitHub clone rebuilt everything on the Pi and passed the self-test 6/6 with the network blocked.

## 2026-10-16 to 2026-10-17: Monitoring dashboard

A dashboard for a phone or computer, started only while someone looks, computing everything in the browser. It grew with the owner's requests: live readings every 3 s, colour signals, a crowned-crow icon and logo, a friendly 🐦 Crow mode next to a detailed 🤓 Nerd mode, links from every friendly figure to its data, a motion-sensor readiness light, the three last checks with photos and a breakdown per visit, problems as small chips in the header, a burst of flowers, fruit and mushrooms for YES (poo for NO), a bear silently playing Hamlet (later removed at the owner's request), an optional password for access from outside (not published for now) and a Power off button ([MONITOR](MONITOR.md)).

Lessons: an alarm shown from a minutes-old health snapshot overstated a 4-second dip, so "power low now" is read live; and the wording swung from too rosy ("mostly fine") to too alarming ("can corrupt the memory card") before settling on the evidence: short dips are notes, because none caused a failure.

## 2026-10-17: Capacitor, power diagnosis and recognition threads

- A 2200 µF capacitor was fitted at the servo. Lining up kernel dips with visits showed that with four recognition threads every visit dipped while photographing and recognising, before the servo moved; the servo's per-move counter had been counting flags left over from recognition. The servo log now records whether a dip began during a move.
- Two threads removed the recognition dips and were faster in real visits (1.27 s instead of about 2 s per photo); a bench check with the detector stopped showed four threads are fastest on their own (0.76 s), so the slowdown came from the sagging supply. Three threads: 0.95 s per photo, YES in 2.6 s, NO in 6.5 s, no recognition dips; now the default.
- With recognition dips gone, the servo's own dips showed: on tilts to the reward side only. A slower servo ramp did not help and was reverted ([POWER](POWER.md#measurements-2026-10-17)).
- All 126 kept visits were reviewed by eye: 113 right, 9 round non-caps accepted, 2 caps missed at the edge of the view. No threshold separates the mistakes; the owner accepted this as a known limit rather than add checks ([RECOGNITION](RECOGNITION.md#review-of-all-kept-visits-2026-10-17-known-limit-accepted)).

## 2026-10-17: Capacitor removed

The owner removed the 2200 µF capacitor at the servo. Over 8 visits without it (3 recognition threads), a dip began during 3 of 16 servo moves, all tilts to the dump side, with no dip while recognising and no failure. With it, the counts had ranged from none to every tilt to the reward side between tests, so it showed no clear benefit ([POWER](POWER.md#measurements-2026-10-17)).

## 2026-10-17: Recognition accepted; energy assessed

28 more visits reviewed by eye (threshold 0.85): all 6 real caps accepted at 0.99–1.00; 15 of 20 other objects rejected; the 5 accepted ones were again round objects seen end-on (a nail-polish bottle standing upright, a round toothpick container, the night light), scored 0.97–1.00, beyond any threshold. The owner is satisfied with how real caps are handled.

Idle load measured on the Pi: 0.5 % of the four cores in total; Tailscale is now the largest single consumer (0.73 % of one core). Energy is dominated by the idle hardware, not the software; the plan for battery operation starts with a USB power meter ([POWER](POWER.md#measured-idle-load-2026-10-17)).

## 2026-10-17: Thread benchmark on 100 visit photos

On the Pi, the same 100 past visit photos with 4, 3, 2 and 1 recognition threads: 0.69, 0.85, 1.18 and 2.18 s per photo. Four threads flagged low power or a capped CPU on 13 % of photos and caused one dip even without camera and light; the others none. The estimated energy differs by about 0.1 % of the daily total between modes, so speed and stability decide: 3 threads stay ([RECOGNITION](RECOGNITION.md#thread-benchmark-100-visit-photos-2026-10-17)).

## 2026-11-20: Sunlight, a self-test regression, new buttons

- **Overexposure in sunlight.** Photos of the sunny hours had a median tray grey level of 220–240 and up to 80 % white pixels (about 70 in the evening): the exposure metered once in the dark stayed fixed. Fix: the exposure is corrected after every photo from the tray's brightness (2–3 ms), see [ALGORITHM](ALGORITHM.md#exposure-control-2026-11-20). Simulated, checked on the real camera in the dark and under a strong lamp (blown-out first photo, right after one correction); the real sun is still to be checked.
- **Self-test regression found and fixed.** Since the threshold could be set from the dashboard (October) the self-test failed with a missing `accept_file`; the running detector was not affected, but a fresh install would have failed its own self-test. Found by running the self-test after the exposure change; it passes 6/6 again.
- **Dashboard:** 🔁 Restart detector and 🔄 Reboot (home network only); the power-bank charge level cannot be read from the Pi, options in [POWER](POWER.md#power-bank-charge-level-in-the-dashboard-2026-11-20).
- **Whole interface from the internet (owner's decision):** threshold, Restart detector and Reboot work behind the password; Power off stays home-only (shown, disabled). New: ⏸ pause, 🍽️ food counter, 📷 live photo with a sharpness number ([MONITOR](MONITOR.md#box-controls)).
- **Verification of a fresh installation and energy cost (owner's request):** a fresh clone is byte-identical with the code on the bench Pi, the units match, the recognition of the six self-test photos from the clone gives the Pi's scores; the additions of the day cost under 0.05 % of the daily energy ([DEPLOY](DEPLOY.md#does-a-fresh-installation-behave-like-the-bench-unit-checked-2026-11-20), [POWER](POWER.md#what-the-additions-of-2026-11-20-cost)). Found on the way: the supply was low at rest (alarm on for minutes, CPU throttled) after the box was re-cabled; two resets that evening were the owner handling the power cables. A colour-cast correction was tested and dropped ([RECOGNITION](RECOGNITION.md#does-the-colour-cast-matter-2026-11-20)).
- **Installation from scratch verified on the bench Pi** (owner's request): self-test 6/6, same scores, same settings afterwards; the permission step waited for a password nobody could type, which stopped the detector for about 20 minutes until the remaining steps were run without it ([DEPLOY](DEPLOY.md#does-a-fresh-installation-behave-like-the-bench-unit-checked-2026-11-20)). README: a new before-and-after section with pictures, and fresh screenshots of the dashboard.

## 2026-11-20: Assessment of the day's session (accepted by the owner as a good result)

**Verdict.** The day's code made nothing worse and improved one condition (bright light); the improvement is shown under a strong lamp, not yet in real sun. A bigger problem found on the way is not caused by the code: the box is slower than on 17 Oct because of the power supply.

| Measure | Before | After |
|---|---|---|
| Tray brightness in the sunny hours (12 visits) | 0 of 12 in range (45-140); 10 of 12 with 5 % or more white pixels; grey 218-242 | strong lamp: 254 → 71 after one correction; a real visit: 6 → 79 |
| Photos in range in ordinary light | 72 % (121 of 168) | 73 % (11 of 15): unchanged |
| Decision time (YES / NO, median) | 2.98 s / 9.44 s | 4.0 s / 10.8 s (10 visits): the supply, see below |
| Self-test | failed since October | 6 of 6 |
| Energy | | +0.016 Wh a day, under 0.05 % |

**Effective:** the adaptive exposure (the cost: one extra photo after an abrupt change of light, about 3 s in the one visit that showed it); the self-test fix, found by running it; Restart and Reboot (Reboot proven by the owner); the live photo (tray area and sharpness for aiming); the check of a fresh installation (code identical by checksum, self-test 6/6, same settings); the measurement of the energy cost.

**Built, not yet proven in use** (on the [roadmap](ROADMAP.md)): pause with a real hand, the food counter, the controls from the internet, the live photo for the new box. Remote control of the threshold, restart and reboot enlarges what the password protects.

**Wasted or a mistake:** the white-balance correction (written, tested on 167 labelled visits, no effect on the recognition, deleted); a heavy experiment run on the box while it was on a power bank, followed by a wrong alarm about "power failures" that were the owner handling the cables; a fresh installation left waiting for a sudo password in a terminal nobody could type into (the detector was stopped for about 20 minutes).

**The finding that was not about the code.** Recognition per photo, median by day: 0.98 s on 17 Oct, 1.61 s on 19 Nov, 1.58 s on 20 Nov before the changes, 1.82 s after. The times inside visits split into a fast mode (about 1.35 s) and a slow one (about 1.85 s), both before and after the changes, as a CPU does that is capped now and then; the Pi reports low voltage and a capped CPU at rest. The supply is the leading suspect for the lost speed (a NO takes about 9.5 s instead of 6.6 s), but this is a **hypothesis**: the CPU clock during a recognition has not been measured, one slow photo (1.96 s) came with three threads confirmed, and the owner considers the supply fine. To be settled by measuring the clock during a visit (needs the owner's approval) and by the A/B test on the roadmap.

## Unexpected hard resets (2026-11-19 to 2026-11-20): findings, cause open

**What happened.** The box restarted by itself without being asked. Every stored boot of the system journal (kept since 17 Oct) was classified as a clean shutdown (the dashboard's Reboot leaves five shutdown records) or an abrupt end:

| End of the run | Last line of the journal |
|---|---|
| 19 Nov 21:12 | "Undervoltage detected!" (91 dips before) |
| 19 Nov 22:17 | cut off (46 dips before) |
| 20 Nov 17:04 | "Undervoltage detected!" (178 dips before); the owner was handling the cables |
| 20 Nov 17:10 | a finished YES visit; the owner was handling the cables |
| 20 Nov 18:18 | a finished YES visit; unprompted |

Five abrupt ends in about 21 hours, none in the stored boots of 17 Oct and none before the evening of 19 Nov, when the box was set up in its new arrangement (power bank fed from the mains).

**Ruled out from the journal:** a software reboot (it leaves records); the hardware watchdog (the next boot began less than 20 s after the last record, the watchdog waits a minute); a crash, out-of-memory or hang (no trace); the SD card (the filesystem only ran its orphan cleanup, no errors); heat (29 °C); a scheduled restart. The detector, the dashboard and the day's changes cannot hard-reset the Pi.

**What remains:** a sudden hard reset within seconds of a visit. In two of the five cases the last thing the Pi wrote was an undervoltage report. For about 19 hours until the owner re-cabled at 17:04 on 20 Nov the Pi's voltage flag at rest was clean; afterwards it showed low voltage continuously (`0x50005`) and the unprompted resets followed. The Pi measures the voltage at its own board, so this says nothing about the mains adapter or the power bank itself, only about what arrives at the Pi.

**The owner's position:** the supply is stable (mains adapter → power bank → system) and the cause should be sought elsewhere. Nothing else was found in the data; no other cause is claimed. The cause is **open**.

**To settle it** (on the [roadmap](ROADMAP.md)): (1) what exactly changed in the cabling at 17:04 on 20 Nov, and put it back; (2) run the box for a couple of hours from the adapter used on 17 Oct, without the power bank: with no resets and about 1 s per photo again the path through the bank was the cause, with resets continuing the search moves to the wiring and the mechanics (the servo's ground and wires, the sensor wires, static discharge); (3) optionally a dashboard note "unexpected restart" (the detector marks a clean stop, writes an abrupt one at the next start with the state of the power flags), not decided.

**Lessons.** Two earlier resets had been read as a power failure when the owner was handling the cables (a false alarm); this time the classification of every stored boot, the timing against the watchdog and the last journal lines were checked first. The journal's tail can be lost in a power loss, so "the reset came right after the visit" is an upper bound, not a fact.

### How well each claim of 20 Nov is supported (self-assessment)

| Claim | Evidence | Status |
|---|---|---|
| The adaptive exposure fixes blown-out pictures | real camera under a strong lamp (254 → 71), one real visit (6 → 79), simulation; no real sun yet | confirmed for the mechanism, sun open |
| The self-test was broken since October and is fixed | the error reproduced, 6/6 after the fix | confirmed |
| Restart, Reboot, live photo work | exercised on the Pi (Reboot by the owner) | confirmed |
| Pause, food counter, controls through the Tailscale address | pause seen in the log only; the others not used; the internet path tested only as a request coming through the proxy | unproven |
| A fresh installation behaves like the bench unit | code identical by checksum, self-test 6/6, same settings; the sudo step ran separately, so the whole in one piece was not seen | confirmed in parts |
| The day's additions cost under 0.05 % energy | measured CPU time, assumed 0.5 W per core, no watt meter | estimate (the order of magnitude is safe) |
| Colour cast does not matter, the correction was dropped | 167 labelled visits, AUC 0.9326 against 0.9304; the correction was simulated on saved photos, not applied in the camera | confirmed, approximately |
| The box's light is blue, not white | one live photo (R 5, G 50, B 118) and the 14 Oct measurement | confirmed |
| The Pi cannot report the power bank's charge | no USB, I2C or power-supply entry on the Pi | confirmed |
| Round objects seen from above are accepted and no threshold separates them | scores of 14 such objects against 99 caps overlap | confirmed |
| The box is slower than on 17 Oct because of the supply | the slowdown is real (0.98 s → 1.6 s per photo, before the day's code); the cause is a flag at rest and a bimodal timing, not a measured clock | **hypothesis** |
| The abrupt restarts are brown-outs | no software trace, two last lines "Undervoltage detected!", onset after the re-cabling; the voltage itself never measured | **probable, not proven; the owner disagrees** |

## Simplification and 3 photos per visit (2026-11-21)

After a review of the last photos and the journal, with the owner's approval to improve recognition and operation without adding constructions: `detect.py` became 62 lines shorter. The background analysis thread, its queue and the photo timetable are gone (photo, analysis, next photo, one after the other), one function takes every photo (start-up, visit, live photo), the options `--photo-interval` and `--fixed-exposure` and two defensive `getattr` fallbacks were removed, and a visit takes at most **3 photos** instead of 5 (no change in any decision on 167 labelled visits, [RECOGNITION](RECOGNITION.md#how-many-photos-per-visit-2026-11-21)). The camera and the recognition no longer run at the same time, which lowers the load peaks on the supply; the effect on speed and on the "Undervoltage" notes is not yet measured. Checked on the setup computer with a stand-in camera and the real model (the same scores as on the Pi, decisions YES at photo 1, YES at photo 3, NO after 3, live photo, no leftover files); then installed on the Pi the same night (files identical by checksum): self-test 6 of 6 correct, YES on photo 1 in 2.4–3.4 s, YES on photo 3 in 5.3 s, NO after 3 photos in 5.3–6.7 s, detector and dashboard running again. The supply still noted three "Undervoltage" dips during the self-test (camera and recognition, no light), so one-after-the-other work did not remove them; live visits are still to be watched.

## Unused system services switched off (2026-11-21)

On the headless box `deploy/trim-system.sh` switched off Bluetooth (service now, radio at the next reboot), the package-manager timers (`apt-daily`, `apt-daily-upgrade`, `man-db`, `dpkg-db-backup`, which started work at random times, possibly during a visit) and `udisks2`. Left alone on purpose: `cloud-init` (it may patch the Wi-Fi settings at boot; losing Wi-Fi on a box without a screen is not worth a faster boot) and `avahi`. The saving is an estimate, 0.05–0.15 W of about 1.4 W idle (no current sensor); updates are now done by hand with `deploy/update_pi.sh`. Not done, owner's choice pending: HDMI and audio off (`vc4-kms-v3d`, `audio=on`; about 0.1–0.15 W).

## Servo module trimmed, HDMI and audio off (2026-11-21)

`servo_bench.py` went from 351 to 305 lines: the shake option of the dump stroke (never used, `shake_count` was always 0), the `--dump-test` bench command and the extra servo-log line written after every visit (the dashboard reads only the lines of single moves) were removed. Checked on the setup computer with a simulated PWM: strokes, return home and a stop in the middle of a stroke behave as before. Kept on purpose: the power-flag reading after every ramp step, because the dashboard's "dip began during the stroke" note depends on it. HDMI (`nohdmi`) and audio were added to `deploy/trim-system.sh` at the owner's decision (no screen or speaker on the box; an estimated 0.1–0.15 W).

Applied on the Pi the same night after a reboot: boot in about a minute, detector and dashboard running, servo at home, start-up photo recognised as a cap (0.95), no Bluetooth timeouts in the journal any more, no HDMI connector in `/sys/class/drm`. The first visits with the trimmed servo module are still to be watched.

First live visits after the change (21 Nov, 7 visits, one object each unless noted): all 7 servo strokes DONE, analysis per photo steady at 0.92–0.94 s (0.9–1.85 s before the change, 0.98 s on 17 Oct), YES on photo 1 in 2.47–2.53 s (5 of 5 single caps), NO after 3 photos in 5.4–5.5 s. The two NO decisions were caps lying with other objects (a crown cap, a yellow lid and a plastic lighter: best 0.83; a cap beside a pair of glasses: best 0.59), the known mixed-scene limit ([RECOGNITION](RECOGNITION.md#how-many-photos-per-visit-2026-11-21)). The kernel still reported about one "Undervoltage" per visit (8 in the first 8 minutes of this boot).

## Trial: servo released between visits (2026-11-21)

At the owner's decision `--servo-idle release` is on in the service file (box and repository): between visits the servo gets no pulses, which saves its holding current (an estimated 0.05–0.25 W, the largest remaining idle item). Risk from the first unit: the tray drifts without pulses and the next stroke begins with a jump. To watch: the tray at rest, the first stroke after a long pause, "Undervoltage" notes at that stroke. Back out: `--servo-idle hold`.

First visits with the servo released (21 Nov, 6 visits): all strokes DONE and back at 1500 µs, 5 YES on photo 1 in 2.5–3.5 s, 1 NO in 6.0 s. In the servo log the undervoltage began *during the stroke* in 5 of 6 reward strokes (`dip_started_during_move`), so the roughly one "Undervoltage" per visit comes from the servo on the Pi's 5 V pin, not from the camera or the recognition (the flags stay set for a while afterwards, which explains an occasional slow photo, 1.5–1.7 s instead of 0.93 s). Known and accepted: the servo stays on the Pi's supply, short dips are notes. Whether the tray drifts without pulses needs the owner's look at the tray after a long pause.

Owner's check after a pause of 5–10 minutes (21 Nov): the tray stays at the centre, the stroke starts without a jump. `--servo-idle release` stays (trial over).

## Check of the latest visits, 21 Nov 02:00 (owner's request)

Visits 8-12 of the boot after the bright-light test: a cap beside glasses accepted at 0.99, a cap lying under glasses accepted at 0.851 (just over 0.85), a crown cap accepted, a cap almost covered by glasses rejected (0.16-0.21), a fork rejected; every decision reasonable, the two weak scores are covered or crowded caps (the known mixed-scene limit). One new finding: the first photo of the visit at 01:18 was almost black (grey level 2) because the exposure was still the bright-light one from the test five minutes earlier (30 ms, gain 1); it recovered in one step (grey 45 on photo 2), so that visit had two usable photos of three. Seen once, after a lamp was switched off; an option if it recurs is to count only usable photos. Also at 02:03:40 the Wi-Fi link dropped and returned by itself within about 2 minutes (signal -66 dBm, the Pi itself kept running, uptime unbroken), which is a network event and not a reset. The dashboard now shows the 12 latest visits (installed on the Pi).

## Right/wrong marks in the dashboard (2026-11-21)

Under every one of the 12 latest checks two buttons, ✔ and ✘, mark the box's decision as right or wrong; the marks go to `config/local.verdicts.json` through a new `POST /api/verdict` (token required, batch name validated, at most 5000 entries) and `GET /api/verdicts`. Purpose: a labelled set of real visits for checking the threshold and, later, for a classifier on the box's own photos, collected by one click instead of by-eye review sessions. About 35 lines in the server and the page; no change in the detector. Checked on the setup computer with a copy of the dashboard and real photos: a valid mark is stored, a bad batch name and a wrong token are refused, a repeated mark clears it, the buttons keep their state after a reload.

## First monthly system update (2026-11-21)

Run by the owner with `deploy/update-system.sh`: the camera stack stayed held back, 31 packages were upgraded, among them openssl, curl, libexpat, liblzma/xz, zlib, libnss3, ca-certificates, tzdata, apt, raspi-config, Tailscale, Wi-Fi and other firmware; no kernel, so no reboot was forced. The first visit after it (02:28) was photographed and analysed normally. Processes started before the update keep the old libraries until they restart, so a reboot at a convenient time completes it (not done yet).

## Latest visits and the real-sun check (2026-11-21)

Visits 18-22 reviewed with the owner. Visits 21-22 held a crown cap upside down and another behind a fork and were rejected (0.13-0.23 on the whole tray); cut out alone they score 0.99-1.00, so the miss is the mixed-scene limit, not the cap. Offline tests on the 167 labelled visits: tiling the tray 2x2 (4 passes per photo) gives 94 % of caps at 18 % others with threshold 0.95, or 85 % at 4 % with 0.99, against 86 % / 19 % now; a slightly tighter tray rectangle gives about +5 points of caps (noise level). The owner declined structural complexity and chose to leave recognition as is. The owner also confirmed that in strong sun the photos are not overexposed, so the adaptive exposure is considered proven; the roadmap item is closed.

## First visits after the reboot, threshold 0.7 (2026-11-21)

The reboot finished the system update (no reboot required afterwards; services up, model loaded in 5 s, servo at home and released between visits). Three visits: a cap at 0.82 was rejected at 0.85 (3 photos, 6.9 s), then the owner set the threshold to 0.7 in the dashboard and kept it; the next caps (0.77, 0.95) were accepted on photo 1 in 2.5-2.8 s. Analysis 0.92 s per photo as before.
