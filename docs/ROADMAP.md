# Roadmap

## Done

- [x] Raspberry Pi 3 running offline: camera, PIR (HC-SR501, settings in [HARDWARE](HARDWARE.md)), RGB light as camera and status light, servo on hardware PWM, calibrated 85° each way.
- [x] Recognition without training: MobileCLIP2-S0 zero-shot, exported to ONNX (ready in about 1.5 s), preprocessing verified.
- [x] Production logic: PIR trigger → up to five photos → YES/NO in 2.6–6.5 s → servo stroke; permanent service that starts at boot and after crashes.
- [x] Grey-card sessions: descriptions, threshold 0.6, self-test photos ([RECOGNITION](RECOGNITION.md)).
- [x] Bench Pi migrated to this project with the one-command installer; self-test 6/6.
- [x] Recognition on 3 cores (2026-10-17): faster in real visits than 4, no power dip while recognising ([MONITOR](MONITOR.md#where-the-power-dips-come-from)).
- [x] One-command installer with self-test, one-command update, persistent system log, storage limits.
- [x] Bench session with caps and lids (2026-10-15): description set chosen; round tray ruled out ([RECOGNITION](RECOGNITION.md)).
- [x] Fixed tray area per unit (`config/local.tray.json`) instead of searching for a round floor.

## Next

- [ ] **Power headroom** (a note, not a fault: no failure seen so far). The servo stays on the Pi's 5 V pin (owner's decision), without a capacitor (tested, no clear benefit, removed); short dips remain on some tilts. To check when convenient: the power supply's rating and cable, and whether the tray meets resistance on the reward side ([POWER](POWER.md#measurements-2026-10-17)). Finding of 2026-11-21: the dips start during the servo stroke (5 of 6 reward strokes), not during photo or recognition.
- [ ] **Energy for battery operation:** measure with a USB power meter first, then night shutdown, Wi-Fi/Tailscale off in the field, HDMI/Bluetooth off, possibly a Pi Zero 2 W ([POWER](POWER.md#measured-idle-load-2026-10-17)). Not needed while the box runs from the mains. Done on 2026-11-21: HDMI, audio, Bluetooth, package timers and udisks2 off (`deploy/trim-system.sh`), servo released between visits. Still open: the USB power meter, to turn the estimates into numbers.
- [x] **`setup_pi.sh --fresh` run on the bench Pi** (2026-11-20): self-test 6/6, same behaviour as before ([DEPLOY](DEPLOY.md#does-a-fresh-installation-behave-like-the-bench-unit-checked-2026-11-20)).
- [x] **Polkit rule installed** by the owner (2026-11-20): 🔄 Reboot works, the Pi came back by itself in 3 minutes after a clean shutdown.
- [ ] **Unexpected hard resets (cause open, 2026-11-19/20):** five abrupt ends in 21 hours, none before; software, watchdog, crash and SD card ruled out ([HISTORY](HISTORY.md#unexpected-hard-resets-2026-11-19-to-2026-11-20-findings-cause-open)). Owner: note what changed in the cabling at 17:04 on 20 Nov and put it back; run a few hours from the 17 Oct adapter without the power bank (A/B); watch whether resets continue. Optional: the "unexpected restart" note in the dashboard. Update 2026-11-21: two more abrupt ends at 00:05 and 00:10 (the second 4 s after a trigger); none in the hours after the simplification, the cause is still open.
- [ ] **Sound at the reward / crow calls (research done 2026-11-21; owner: no sound test now, kept as a future technology):** no validated crow vocabulary exists and playback evidence is mixed. If it is ever built: a neutral chime at the reward, tested on alternate weeks by visit counts, never alarm calls. Hardware, cheapest and simplest first: (1) active buzzer module with a 3-pin socket, 5 V from the Pi, signal on GPIO24, about 3.5 €, no amplifier and no extra supply, beep only; (2) MAX98357A I2S amplifier with a miniature 4 Ω 3 W speaker (2.94 € in the listing) for recorded sounds, about 8-10 €, the servo PWM then moves from GPIO 18 to GPIO 12 ([CROW-CALLS](CROW-CALLS.md)).
- [ ] **Optional, not recommended without evidence:** cap the CPU at about 900 MHz to lower the load peaks (the photo would take about 1.2 s instead of 0.93 s); only if the dips turn out to come from the processor.
- [x] **Speed regression (found 2026-11-20): gone after the change of 2026-11-21.** Recognition per photo was 1.6 s on 19-20 Nov against 0.98 s on 17 Oct; since photo and analysis run one after the other it is a steady 0.92-0.94 s, although the supply still dips about once per visit. So the cause was the overlap of the camera and the recognition (and not the supply alone); the CPU clock was never measured and no longer needs to be ([HISTORY](HISTORY.md)).
- [ ] **Built on 2026-11-20 but not yet proven in use** (to be ticked off one by one):
  - Pause with a real hand at the tray: while paused no visit and no stroke; after Resume a visit again.
  - Food counter: enter the real capacity, refill, check that the number goes down with the rewards and that the note appears at 15 %.
  - Controls from the internet through the Tailscale address (threshold, Restart, Reboot, Pause, Live photo behind the password; Power off disabled there).
  - Live photo used for the new box: tray area and focus set by its outline and sharpness number.
- [ ] **Check the adaptive exposure in real sun** (2026-11-20; under a strong lamp it worked: grey 254 → 71 after one correction): visits around midday; the dashboard shows each photo's exposure and grey level; the tray should come out near 90 instead of 220–240.
- [ ] **Power bank charge level:** INA226 current sensor on I2C, energy used since the last charge, estimated percentage ([POWER](POWER.md#power-bank-charge-level-in-the-dashboard-2026-11-20)); waits for the owner's choice of sensor.
- [ ] **Intake height limit (about 25 mm)** against upright cylinders and tall objects, the largest group of false YES ([RECOGNITION](RECOGNITION.md#can-the-recognition-be-improved-2026-11-20)).
- [ ] **Round non-cap objects** are sometimes accepted (known limit, accepted 2026-10-17). A model trained on the box's own photos would fix it if it ever matters.
- [x] **Licence:** all rights reserved; permission on request (free for private individuals, commercial licence for public authorities and companies) ([LICENSE](../LICENSE)).
- [x] **Repository public** (for viewing), 2026-10-15.
- [ ] **A recognition model under a business-friendly licence** before any sale: Apple's MobileCLIP2 licence allows only non-commercial research, including the exported model. Candidates: CLIP-type models under MIT or Apache-2.0 (for example OpenAI CLIP, TinyCLIP), measured for speed on the Pi 3; or a small model trained on our own photos with a permissively licensed backbone. Same tests as now (grey-card sessions, self-test).

- [x] **Monitoring dashboard** (2026-10-17): on demand, computed in the browser; Crow and Nerd modes, last checks with photos, motion-sensor readiness, power-dip diagnosis, optional password, Power off button ([MONITOR](MONITOR.md)).

## Open decisions

- [ ] **Set-up step per unit**, run by the installer (no manual photo collection): an empty-tray photo that sets the tray area and records the expected brightness and sharpness; a one-minute YES/NO check with a real cap and another object; periodic comparison with the empty-tray photo, to catch a shifted camera, a dirty tray or a fogged window. The shipped self-test photos stay the same for every unit.
- [ ] **Dark photos.** Nearly black photos are still judged instead of being rejected as bad images and taken again with a new exposure.
- [ ] **The owner's "growing area" tactic.** Each photo (three now) is analysed on a slightly larger part of the tray than the one before. One area per photo, so the time per photo stays the same; an object at the edge is found on a later photo, and the widest areas give the model more distractions. Test offline on saved visit photos first (caps found, time to YES, false YES).
- [ ] **Physical prototype box** (owner, from 2026-10-17): one servo, powered from the Pi, camera and light placed by the owner, PIR zone limited. After assembly: camera focus, servo calibration, new tray area, self-test, then 20–30 test visits to re-check the threshold (0.85) on the new tray and light ([DEPLOY](DEPLOY.md), step 6). Settings of the bench mock-up are backed up on the setup computer.
- [ ] **From [MECHANICS](MECHANICS.md):** one or two servos, ledge height, food type, and whether the dish needs a shutter.

## Version 2: a device that trains crows step by step (to do, owner 2026-10-15; to be studied later)

Version 1 rewards a crow for a deposited bottle cap. Version 2 should also lead crows to the habit on its own, building on Joshua Klein's four training stages.

| Stage | Device behaviour | Moves on when (example, to be set with an ornithologist) |
|---|---|---|
| 0. Getting used to it | Box present, food in the dish, no motors moving | Crows feed regularly (expect weeks: crows are wary of new objects) |
| 1. Free food | Dispenser adds food on a timer | Visits on most days |
| 2. Food on landing | Food only when a bird lands | Several landings a day for 3 days |
| 3. Caps provided | A cap presenter puts a cap on the ledge. Any cap entering the slot earns food, even by accident. Deposited training caps return to the presenter. | Several deposits a day |
| 4. Fading | The presenter offers caps less often; caps lie around the box | Deposits keep up as provided caps drop |
| 5. Full use | Only found caps, with a daily reward limit | Falls back a stage if deposits stop |

- [ ] **Instant feedback.** Recognition takes 3–8 s, which weakens the link between deposit and reward.
  - Give a soft click or flash the moment an object drops, like clicker training. An infrared beam across the slot detects any drop instantly.
  - In stages 3–4, reward any deposit at once; require recognition only once the habit exists.
- [ ] **Hardware:**
  - cap presenter with a magazine;
  - load cell under the ledge, to detect landings and tell crows from pigeons by weight;
  - small speaker;
  - infrared beam across the slot;
  - real-time clock module, because an offline Pi loses the time after a power cut, and daily reward limits, schedules and statistics need it;
  - optionally a second camera on the ledge (a Pi 5 has two camera ports).
- [ ] **Software:**
  - stage logic with automatic progression and fallback;
  - learning curves per stage;
  - settings changeable without network;
  - statistics on a phone over Bluetooth Low Energy.
- [ ] **Research:** stage criteria and welfare limits with an ornithologist. Use social learning by choosing sites where crows already gather.

## Later phase

Enclosure (reference design and build/test plan: [MECHANICS](MECHANICS.md)), weather/pinch protection, waste/food hygiene, motion-area clearance, reward limits, observation protocol, and necessary approvals before bird trials. Behavioral/animal-welfare research is separate; mass deployment and food additives are outside v1.
