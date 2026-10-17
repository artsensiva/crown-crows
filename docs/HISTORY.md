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
