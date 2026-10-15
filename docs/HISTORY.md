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
