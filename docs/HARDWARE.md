# Hardware and wiring

## v1 bill of materials

| Component | Quantity | Purpose and status |
|---|---:|---|
| Raspberry Pi 3 Model B (1 GB) | 1 | Main controller; runs everything offline |
| microSD card, 8 GB or more (A1 or better) | 1 | Operating system, engine, photos and logs ([DEPLOY](DEPLOY.md#storage-needed)) |
| Camera Module V2, IMX219 | 1 | Photos of the tray, exposure fixed once per start |
| Standard 15-pin CSI ribbon | 1 | Pi 3B to camera |
| PIR HC-SR501 (identified from the board, 2026-10-14) | 1 | Settings: see "PIR settings" below |
| JAMARA High End Micro 033212 servo | 1 | 4.8–6 V; manufacturer max 600–750 mA; calibrated 605 / 1500 / 2500 µs ([SERVO](SERVO.md)) |
| RGB LED module (common anode) | 1 | Camera light and status light on GPIO27/22/23; a brighter white light is planned ([LIGHTING](LIGHTING.md)) |
| Pi supply | 1 | Target: quality 5–5.1 V, 2.5 A micro-USB supply and sound short cable |
| Separate servo supply | 1 | Match servo specification, including startup/stall demand |
| Jumper wires or a soldered board | Set | Secure connections without exposed short-circuit hazards |
| Tray, waste bin, food dispenser | Set | Design study in [MECHANICS](MECHANICS.md); it recommends a second servo for the food portioner (GPIO19, second hardware PWM channel) instead of one servo for both routes |


## Power and shutdown

Run `sudo poweroff` on the Pi. Wait for shutdown completion (normally 30–60 seconds and cessation of ACT activity), then disconnect Pi and servo power. SSH disconnection alone is not confirmation of complete shutdown. The red LED may remain on while power is attached.

Change CSI and GPIO wiring only with all power disconnected. Do not power the servo from signal GPIO, 3.3 V, or, in this prototype, the Pi's 5 V pin. Do not join the positive servo supply to Pi 5 V; join grounds. Never apply 5 V to signal GPIO.

Replacing the cable is diagnostic, not proof that ThinkCentre USB power is sufficient. Check `vcgencmd get_throttled`: active undervoltage/throttling flags must clear; historical flags persist until reboot. Stable power under load is required before mechanical tests.

## Pin assignments

Software uses **BCM numbering**; physical pin numbers refer to positions on the 40-pin header. Locate pin 1 using board markings or the official diagram, not an arbitrary corner.

| Device | Terminal | Pi pin / connection |
|---|---|---|
| HC-SR501 PIR | VCC | Physical 2, 5 V |
| PIR | OUT | Physical 11, GPIO17; output must be 3.3 V |
| PIR | GND | Physical 6, GND |
| Servo | Signal | Physical 12, GPIO18 |
| Servo | V+ | Separate supply matching its specification (currently, 2026-10-14, the Pi's 5 V pin; see [POWER](POWER.md)) |
| Servo | GND | Servo supply negative and physical 9, Pi GND |
| IDUINO RGB | U, common anode | Physical 1, 3.3 V, not 5 V |
| IDUINO RGB | R | GPIO27, physical 13 (onboard 330 ohms; external 220 ohms removed 2026-10-14) |
| IDUINO RGB | G | GPIO22, physical 15 (onboard 330 ohms; external 220 ohms removed 2026-10-14) |
| IDUINO RGB | B | GPIO23, physical 16 (onboard 330 ohms; external 220 ohms removed 2026-10-14) |
| Camera V2 | Ribbon | CAMERA/CSI, not GPIO or DISPLAY |

**Physical pin 10 is GPIO15, NOT ground.** Do not reproduce the error in an early sketch.

### Camera Module V2

On Pi 3B, CAMERA is between HDMI and the audio jack. With power removed, gently lift the latch, insert the standard 15-pin ribbon straight with exposed contacts facing the connector contacts, and close the latch. On a standard Pi 3B exposed ribbon contacts face HDMI. At the camera end they face the camera board. Do not rely solely on the stiffener color of a nonstandard cable.

After power-up, run `rpicam-hello --list-cameras`; expect IMX219. A missing camera does not prove failure: check power, seating, and orientation. V2 with libcamera does not require the legacy camera stack.

### PIR

Read the module's VCC/OUT/GND labels; pin order can differ. The module is an HC-SR501 (two "105" potentiometers and a yellow H/L jumper). Allow its warm-up time after power-on (the detector waits 60 s).

A PIR detects changes in thermal radiation from warm moving bodies, not the deposited objects: it wakes the system when a crow's head (or a hand) moves near the intake, and the camera decides what was deposited (see [ALGORITHM](ALGORITHM.md)).

#### PIR settings (owner, 2026-10-14)

| Control | Function | Setting |
|---|---|---|
| Sensitivity potentiometer (Sx) | Detection range, nominally about 3–7 m | **Fully anticlockwise** (minimum) |
| Time potentiometer (Tx) | How long the output stays HIGH after the last motion | **Fully anticlockwise** (shortest); the output stays HIGH about 0.9 s after the last motion (measured 0.92–0.93 s) |
| Jumper H/L | **H** = repeat trigger: the output stays HIGH while motion continues; L = single pulse that ends after the set time even if motion continues | **H** |

Why these settings:
- **H** makes one visit one trigger. The detector starts a cycle on a rising edge, ignores triggers for 25 s, and needs a LOW before the next cycle, so a crow that stays a long time does not start a second photo series and servo stroke while it is still at the box. With L it would.
- **Shortest time:** the detector only needs the start of the motion; a long HIGH would only delay re-arming.
- **Minimum sensitivity:** with both potentiometers at minimum, a quick hand movement triggered the sensor only within about 50 cm. Slower movements or a larger warm body (a crow) may be detected somewhat further away; test with slow movements as well.

Which potentiometer is which, and which jumper position is H, varies between board versions: read the small markings on the board (often "Sx"/"Tx" and "H"/"L"). A quick check for the jumper: keep a hand moving in front of the sensor for about 10 s; with H the output stays HIGH throughout, with L it switches off and on.

#### Limiting the trigger zone to about 35 cm

The sensitivity potentiometer changes how strong a signal must be, not a distance limit: an HC-SR501 at minimum sensitivity can still react to warm movement a few metres away, and a crow at 35 cm always produces a strong signal. To make it react only near the intake, restrict **what it sees**:

1. **Tube or shroud.** Mount the sensor at the end of a short opaque tube (for example 3–5 cm long, slightly wider than the dome), aimed at the place where the crow's head will be at the opening. Anything outside that cone is invisible to the sensor.
2. **Mask the lens.** Opaque tape over parts of the white Fresnel dome narrows the field of view further.
3. **Aim it close and sideways or downwards** at the opening, so that the street, the sky and passers-by are not in view. A shroud also reduces false triggers from sunlight on the dome or from warm surfaces nearby.

If a precise distance limit is needed later, a different sensor can measure distance, for example a small time-of-flight distance sensor (such as the VL53L0X, "trigger only below 35 cm") or an infrared light barrier across the opening; both also detect cold objects such as a cap. These are options to investigate, not part of the current build (see [MISSION](MISSION.md#7-mechanics-and-robustness)).

### Servo

JAMARA 033212 micro servo on hardware PWM (GPIO18), calibrated to 85° each way ([SERVO](SERVO.md)). Powered from the Pi's 5 V pin (kept so by the owner), with a 2200 µF capacitor across its supply wires since 2026-10-17; short undervoltage dips remain on tilts to the reward side, without failures so far ([POWER](POWER.md#measurements-2026-10-17)).

Common colors: red for power, brown/black for ground, yellow/orange/white for signal. Verify against the model rather than color alone. Confirm it is positional: continuous-rotation servos interpret pulses as speed, not HOME position.

Initially test without horn or load, within a limited documented pulse range. Calibrate HOME and both directions against mechanical stops. Do not assume universal 0/90/180-degree limits. Without feedback, software knows the command, not actual position or successful food delivery.

### LED and 220R 5% resistors

The current module is a common-anode IDUINO RGB with three onboard 330-ohm
resistors visible in the photo. The additional external 220 ohms per channel
were removed on 2026-10-14 to brighten the light. The bare-LED example below
is background, not the current wiring. A brighter white light is planned
([LIGHTING](LIGHTING.md)).

A bare low-power LED requires a series resistor. `220R 5%` means 220 ohms ±5%, not its power rating. Calculate `R = (3.3 V − Vf) / I` using the LED specification and GPIO current limits.

Three 220-ohm resistors in series give 660 ohms. At Vf around 2 V, current is approximately 2 mA; brightness varies. Connect GPIO → resistor(s) → anode; cathode → GND. A single 220-ohm resistor is not universally suitable.

Do not power a high-power light, strip, or module directly from GPIO. Select a suitable supply/driver and switching circuit, such as an appropriate MOSFET, after identifying the load. A small indicator may not adequately illuminate the camera scene.

## Bring-up order

Power → camera → PIR → LED → unloaded servo → mechanics → full cycle. Shut down and remove all power before each wiring change. Never run the servo during active undervoltage.

## Sources

- [Official camera installation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [Raspberry Pi GPIO and power](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [GPIO Zero recipes](https://gpiozero.readthedocs.io/en/stable/recipes.html)
