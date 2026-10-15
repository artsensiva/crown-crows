# White light upgrade

Status (2026-10-14): planned; software ready (`--lights white`), hardware not yet built. Switch off and unplug all power before changing any wiring.

## Why

Measured in the covered box with the current IDUINO RGB module (common anode on 3.3 V, about 550 ohms per channel):

- With our LEDs off the tray is black, so the module is the only light. At a fixed exposure it gives R 6, G 61, B 103: dim and strongly blue (red and green channels get far less current than blue).
- Auto-exposure needs 60 ms (the longest it chose) at analogue gain 4.2–5.4. Long exposure blurs anything still moving; high gain adds noise.
- Auto white balance does not settle consistently under this light: start-up calibrations chose red/blue gains from 1.42/1.69 to 2.20/1.26.
- A brighter, neutral light gives sharper photos and lets the camera use a short exposure.

## Interim step taken

On 2026-10-14 the owner removed the external 220-ohm resistors from the RGB module, leaving its onboard 330 ohms: about 1.6 times the current per channel. The owner saw a brighter light. A measurement was inconclusive because room light was leaking into the box (with our LEDs off the tray measured R 115–121, G 58–60, B 2 instead of black), and the auto-exposure still chose 55–60 ms at gain 4.0–4.5. The colour stays blue-heavy, so the white strip below remains the real fix.

## What to build

A short **white LED strip** around the camera at the top of the tube, pointing down, switched by a **logic-level N-MOSFET** from GPIO27, powered by its **own 5 V supply**.

| Part | Recommendation | Notes |
|---|---|---|
| Light | 5 V white LED strip, 10–20 cm (6–12 LEDs), 4000–5000 K, CRI 90+ if available; a COB strip gives the most even light | Roughly 0.5–1.5 W, 100–300 mA at 5 V. Tens of lumens, against well under one lumen now. A 12 V strip also works with a 12 V supply and the same circuit. |
| Switch | Through-hole logic-level N-MOSFET, e.g. IRLZ44N, IRLB8721 or IRL540N | Must be specified for low gate voltage (on-resistance given at 4.5 V or lower, gate threshold at most about 2 V). A standard IRFZ44N (without "L") is **not** suitable at 3.3 V. |
| Gate resistor | 100 ohm | Between GPIO27 and the gate. |
| Gate pull-down | 100 kilohm | Between gate and source; keeps the light off while the Pi boots or if the wire comes loose. |
| Supply | Separate 5 V, at least 1 A (USB charger with a cut USB cable or a 5 V adapter) | Not the Pi's 5 V pin: the Pi has already shown undervoltage. Ground must be joined to the Pi's ground. |
| Optional | 470 µF capacitor across the strip supply; diffuser (tracing paper or frosted plastic) | The diffuser avoids bright spots and reflections on the floor. |

## Wiring

```
5 V supply (+) ──────────────────────────── LED strip (+)
                                             LED strip (−) ── MOSFET drain (D)
5 V supply (−) ──┬── MOSFET source (S)
                 └── Pi GND (physical pin 14)
Pi GPIO27 (physical pin 13) ── 100 Ω ── MOSFET gate (G)
MOSFET gate (G) ── 100 kΩ ── MOSFET source (S)
```

For IRLZ44N, IRLB8721 and IRL540N (TO-220), looking at the printed side with the legs down, the pins are **G, D, S** from left to right. Check the datasheet of the part you actually have.

1. Remove the RGB module: disconnect its U lead from physical pin 1 (3.3 V) and its R, G, B leads (and their 220 ohm resistors) from GPIO27, GPIO22 and GPIO23 (physical pins 13, 15, 16).
2. Build the circuit above. Check the strip's + and − markings.
3. Mount the strip around the camera lens, facing down, with the LEDs not directly visible to the camera; add the diffuser if the floor shows bright spots.
4. Before connecting the Pi: power only the 5 V supply and confirm the strip stays dark. Touching the gate side of the 100 ohm resistor to the supply's + for a moment should light it.

GPIO27 is pulled low by the Pi itself at power-up, and the 100 kilohm resistor holds the gate low as well, so the light stays off during boot. This also removes the faint boot-time glow of the RGB module.

## Switching the software over

The scripts select the light hardware with `--lights`: `rgb` (default, the current module: GPIO27/22/23, active-low) or `white` (GPIO27 only, active-high). After the hardware is built:

1. Add `--lights white` to `ExecStart` in `deploy/crown-crows-detect.service`, copy it to `~/.config/systemd/user/`, then `systemctl --user daemon-reload` and `systemctl --user restart crown-crows-detect`.
2. Check the start-up photo in the newest `captures/<boot>-0000-<pid>/` folder: the light should be neutral, and the logged exposure should be far shorter than 60 ms at a lower gain.
3. Repeat the recognition checks on an empty tray, a cap and another object.
4. Once the light is stable, fix the white-balance gains in configuration instead of measuring them at every start.

Software was verified with gpiozero mock pins: for `white`, GPIO27 is low when off, high when on and low again after the program exits; `rgb` behaves as before (high when off, low when on, high after exit).
