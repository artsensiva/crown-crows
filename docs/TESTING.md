# Manual test from a cold start, without network

This checks the whole system the way it will run in the field: power on, no network, no setup computer, crows (here: your hand) arriving at the box. The Pi records everything on its SD card, so the results are read afterwards, once the network is back.

## 1. Prepare

- Box covered, camera aimed at the tray, tray empty, tray area set ([DEPLOY](DEPLOY.md)).
- Servo supply ready (5–6 V), mechanism clear.
- A list of test objects and a way to note the order and what you saw, for example:

| # | Object | Expected | Servo seen |
|---|---|---|---|
| 1 | crown cap, logo up | YES, counter-clockwise | |
| 2 | plastic cap, upside down | YES | |
| 3 | piece of paper | NO, clockwise | |
| 4 | leaf or twig | NO | |
| 5 | hand only, nothing dropped | NO | |
| 6 | cap at the edge of the tray | YES | |

## 2. Take the Pi off the network

Choose one:
- **Switch off the Wi-Fi router** (simplest; other devices lose the network too).
- **Move the box out of Wi-Fi range.**
- **Switch Wi-Fi off on the Pi** before the test: `sudo nmcli radio wifi off`. This survives reboots; to switch it back on you need a keyboard and monitor on the Pi (`sudo nmcli radio wifi on`).

## 3. Cold start

1. Switch off the servo supply.
2. Unplug the Pi's power (a field-like power cut), wait 10 s, plug it back in.
3. Switch the servo supply on again.

What you should see:
- After about 30–40 s (boot), the light shows blue; it briefly turns white while the exposure is measured and the start-up photo taken.
- The servo moves to, or stays at, the centre and holds it.
- Blue blinking during the 60 s motion-sensor warm-up, then **three green flashes: ready**, about 2 minutes after power-on. The light then stays dark, except white while photos are taken.
- A red blip every 5 s means it runs without the servo; fast red blinking means it stopped with an error and restarts itself 30 s later.

## 4. Visits

For each object:
1. Put it into the intake by hand, so your hand passes in front of the opening as a crow's head would, and pull your hand out.
2. About 1 s later the light comes on and photos are taken.
3. **YES** (cap or lid): counter-clockwise stroke about 2.7–5 s after your hand arrived. **NO**: clockwise stroke after about 7.5 s. The servo holds 0.5 s, returns to the centre and holds the tray there.
4. Note what you saw, then **wait at least 25 s** before the next object: triggers are ignored for 25 s after each visit.

## 5. Read the results

Switch the network back on, connect from the setup computer, and on the Pi:

```bash
cd ~/crown-crows && .venv-detector/bin/python -B report.py                       # visits since this boot
journalctl -b --user -u crown-crows-detect --no-pager -o cat | head -20          # service start-up
journalctl -k -b --no-pager | grep -i -E "voltage|error"                         # power and kernel problems
```

`report.py` lists every visit with its decision, the number of photos, the best score and the photo it came from, the time from trigger to decision, and the servo stroke. The photos are in `~/crown-crows/captures/<batch>/`. Times are relative; the Pi's clock is not reliable offline.

## 6. Pass criteria

- The service started by itself after the cold start, without network.
- Every visit produced exactly one decision and the matching stroke.
- Every clearly visible cap gave YES; paper, leaves, twigs and an empty tray gave NO.
- Decisions within about 5 s for YES and 8 s for NO.
- No "Undervoltage detected" and no crash during the test.

Record the result, with the object list and the `report.py` output, in [HISTORY](HISTORY.md).
