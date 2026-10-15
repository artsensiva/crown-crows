# Roadmap

## Done

- [x] Raspberry Pi 3 running offline: camera, PIR (HC-SR501, settings in [HARDWARE](HARDWARE.md)), RGB light as camera and status light, servo on hardware PWM, calibrated 85° each way.
- [x] Recognition without training: MobileCLIP2-S0 zero-shot, exported to ONNX (ready in about 1.5 s), preprocessing verified.
- [x] Production logic: PIR trigger → up to five photos → YES/NO in 2.7–7.5 s → servo stroke; permanent service that starts at boot and after crashes.
- [x] One-command installer with self-test, one-command update, persistent system log, storage limits.
- [x] Bench session with caps and lids (2026-10-15): description set chosen; round tray ruled out ([RECOGNITION](RECOGNITION.md)).
- [x] Fixed tray area per unit (`config/local.tray.json`) instead of searching for a round floor.

## Next

- [ ] **Grey-card test on the bench:** a plain grey card as the tray floor, caps and lids, other objects, empty tray. Sets the threshold, decides whether "jar lid" joins the cap descriptions, and provides the self-test photos (`selftest-photos/`, with `tray.json`).
- [ ] **Migrate the bench Pi** to this project, installed like any other unit; self-test, then a live test with caps ([TESTING](TESTING.md)).
- [ ] **Separate servo supply** (power bank port or regulator); the Pi reported undervoltage while powering the servo ([POWER](POWER.md)).
- [ ] **Choose a licence**, then publish the repository.

## Open decisions

- [ ] **Set-up step per unit**, run by the installer (no manual photo collection): an empty-tray photo that sets the tray area and records the expected brightness and sharpness; a one-minute YES/NO check with a real cap and another object; periodic comparison with the empty-tray photo, to catch a shifted camera, a dirty tray or a fogged window. The shipped self-test photos stay the same for every unit.
- [ ] **Dark photos.** Nearly black photos are still judged instead of being rejected as bad images and taken again with a new exposure.
- [ ] **The owner's "growing area" tactic.** Each of the five photos is analysed on a slightly larger part of the tray than the one before. One area per photo, so the time per photo stays the same; an object at the edge is found on a later photo, and the widest areas give the model more distractions. Test offline on saved visit photos first (caps found, time to YES, false YES).
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
