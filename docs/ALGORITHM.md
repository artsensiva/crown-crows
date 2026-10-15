# Operating algorithm

## One visit

1. **PIR trigger.** The motion sensor fires when a warm body (a crow's head, a hand) moves in front of the intake. Further triggers are ignored for `--ignore-seconds` (25 s: 1 s pause + 5–7 s analysis + about 10 s for the crow to take the food and leave, rounded up).
2. **Photos.** Wait `--first-delay` (1 s) so the object has landed, switch the light on, then take up to `--photos` (5) photos `--photo-interval` (1 s) apart. The light goes off after the last photo, or as soon as the decision is YES.
3. **Recognition.** Each photo is analysed in a background thread as soon as it is taken (pipelined: the next photo is taken while the previous one is analysed). Only the unit's fixed tray area is analysed ([RECOGNITION](RECOGNITION.md)); its `cap_score` is the model's probability that the picture shows a bottle cap.
4. **Decision.** **YES** as soon as any photo reaches `--accept` (0.6): no further photos, reward stroke (`dump_reward`, counter-clockwise). **NO** if none of the five does: dump-only stroke (`dump_only`, clockwise). Either way the servo holds the end position for `--dump-seconds` (0.5 s) and returns straight to the centre, where it holds the tray until the next visit.
5. **Record.** Each visit's photos are kept in `captures/<boot>-<sequence>-<pid>/` (the oldest are deleted beyond 1000 visits), and one line in `logs/detect.jsonl` records every photo's score and top label, the decision, the time from trigger to decision and the stroke.

At start-up the servo moves to the centre, the light measures the exposure once (it then stays fixed, so each photo is taken immediately), and one photo of the empty tray is saved as `captures/<boot>-0000-<pid>/` so the aim and the tray area can be checked after every start. After a 60 s PIR warm-up the light flashes green three times: ready.

## Why it is built this way

| Finding on the bench | Consequence |
|---|---|
| A PIR does not detect cold objects: six objects tossed into the intake gave zero PIR pulses; a hand always triggers it | The PIR only wakes the system; the camera decides what arrived |
| A photo taken at the trigger can show the object mid-fall | First photo 1 s after the trigger, then more photos: any one of them may decide |
| The model loads in about 1.5 s and stays in memory; one analysis takes 0.75–1.4 s on the Pi 3, one photo 0.45–0.7 s | Pipelined photos and analysis: a YES in 2.7–5 s, a NO after about 7.5 s |
| Room light reaching the tray changed scores drastically | The intake must be dark; the box's own light is the only light |
| The model judges the whole picture, not objects inside it: whole photos with walls and other objects in view scored a clearly visible object at 0.02, a crop of the tray at 0.99 | Analyse only the tray area, fixed per unit ([DEPLOY](DEPLOY.md)) |
| Seen from above, a round floor inside a round tube looks like a cap: empty trays scored up to 0.99 as "bottle cap" | Square or rectangular, plain grey tray; no round shapes in the analysed area ([MECHANICS](MECHANICS.md)) |
| Searching for a round floor in every photo failed on other trays and would lock onto a cap itself | No searching: a fixed tray area per unit |

**Accepted risk:** "any one of five photos" gives more chances, so an object that only briefly looks like a cap can earn a reward. Long-term reliable operation is preferred over avoiding every occasional error. Objects that are not caps but are rewarded anyway (coins, washers, buttons) are not a problem for now.

## Timing

| Step | Time |
|---|---|
| Trigger → first photo | 1 s |
| Photo (fixed exposure, `--immediate`) | 0.45–0.7 s |
| Analysis of one photo | 0.75–1.4 s |
| YES on photo 1 / photo 3 | about 2.7 s / 5 s after the trigger |
| NO (all five photos) | about 7.5 s after the trigger |
| Servo stroke out, 0.5 s hold, back | about 1.2 s |
