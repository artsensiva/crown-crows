# Field pilot plan: from the bench to real crows (draft, 2026-11-21)

The bench box recognises caps reliably enough. What no test has shown yet is whether **wild crows come, accept the box and learn to bring caps**. This plan is a draft for the owner to correct. Its stages are an inference from the research below plus common practice in feeding and training birds, not a validated protocol (no validated protocol for wild crows was found); the 2008 crow vending machine is no evidence either way, as corvid researchers disputed its claims ([NPR](https://www.npr.org/2008/03/04/87878028/inventor-trains-crows-to-find-money); [Kottke](https://kottke.org/09/04/no-vending-machine-for-crows)).

## What the research says that matters for the plan

- **Adult carrion crows and ravens are highly neophobic**: they hesitate to feed beside a new object ([Miller et al., Current Biology 2022, 10 corvid species](https://homepages.uni-tuebingen.de/andreas.nieder/Miller%20et%20al.%20(2022)%20CurrBiol.pdf); [ravens and carrion crows across development](https://link.springer.com/article/10.1007/s00265-015-1935-8)). A new box next to the food is the thing they will fear first.
- **Habituation first.** Field protocols bait the site with familiar food for a while before any new object; the review of corvid neophobia advises habituating until the latency to feed beside the new item matches the baseline latency ([Current Biology review](https://www.cell.com/current-biology/fulltext/S0960-9822(21)01468-8)). A wild American crow study needed 1-7 days of pre-conditioning at some sites ([Swift and Marzluff](https://corvidresearch.blog/wp-content/uploads/2015/09/swift_marzluff_crows.pdf)); urban crows may be *more* neophobic than rural ones ([Behavioral Ecology 2026](https://academic.oup.com/beheco/article/37/6/arag135/8965428?login=false)), while across species urban living went with *less* object neophobia, so the site matters and cannot be predicted. Plan for weeks, not days.
- **Crows learn dangers from others, quickly** (scolding spreads between crows). One frightening event at the box (a person, a noise, a trapped bird) can end the pilot, so avoid surprises.

## Stages (go on only when the criterion is met; a stage may take weeks)

0. **Before anything.** Check local rules for feeding wild birds and for placing objects on the site (city or housing rules; no general German ban on feeding carrion crows was found, but cities and parks differ, [Berlin](https://www.berlin.de/lb/tierschutz/wildtiere/artikel.1379720.php); Munich's own guidance even advises against feeding crows because they lose their shyness, [City of Munich](https://stadt.muenchen.de/dms/Home/Stadtverwaltung/Kreisverwaltungsreferat/fachspezifisch/HA-I/Jagen-Fisch-Waffen/Dokumente/Rabenkraehen.pdf)). Think of neighbours, rats (never leave food overnight in the open) and a quiet site with regular crow traffic and a view.
1. **Habituate to the place, no box.** The same food (unsalted, unseasoned; for example peanuts in the shell, a common choice, not verified here), the same spot, about the same time each day. *Criterion:* crows land and eat within a minute or so, on most days for a week.
2. **Box present, switched off.** The dead box beside the food (no light, no servo, detector paused from the dashboard). *Criterion:* crows eat beside it as fast as before.
3. **Box on, food only.** Light and servo active, food in the tray area or beside it, so the strokes and the light become normal events. This needs a free-food mode that the code does not have yet (today the reward is released only for a recognised cap); to be decided with the owner before this stage. *Criterion:* no flight reaction to the light or the stroke.
4. **Caps near the food.** Caps lying next to the box and food; crows handling caps ([crown caps have sharp crimped edges: prefer plastic caps and lids, and check every cap for edges and dirt](RECOGNITION.md)). The slow step, where the learning of "cap in the tray gives food" happens, with unknown odds.
5. **Only caps give food.** The normal operation of the box.

**Stop and rethink if** after about three weeks in one stage there is no progress, or if crows avoid the place. A failed stage is a result, not a defect of the box.

## What to count (from the existing logs and the dashboard)

| Question | Where |
|---|---|
| Does anything come at all, and when? | visits per day and per hour in `logs/detect.jsonl` (the dashboard's visits list) |
| Are the triggers crows? | the 12 latest checks with photos; false triggers (people, cats, leaves, wind) are common with a PIR |
| Do they return? | gaps between visits on the same day; repeat visits within minutes |
| Do they understand the box? | the share of visits with a cap and of YES; first YES by a crow (photo check) |
| Is the box safe for them? | every day, a look at the photos for trapped or injured birds and objects stuck in the tray; the servo-stroke log for failed strokes |

There is no way to tell individual crows apart yet; colour-marking is not planned and would need the care of a licensed ringer.

## Open decisions for the owner

1. The site, and the rules there (stage 0).
2. A free-food mode for stage 3 (small code change, not made).
3. Food and cap types (plastic caps first).
4. Whether the dashboard should show per-day visit counts (the logs hold them; a small chart would make stage progress visible).
