# Recognition

## Model

**MobileCLIP2-S0** (Apple), used zero-shot: no training on our photos. The model turns a picture into a list of numbers that describes what it looks like, and does the same with short text descriptions. The description closest to the picture wins. Our descriptions are in `recognition.py`:

| Group | Descriptions | Meaning |
|---|---|---|
| Caps and lids (summed into `cap_score`) | "bottle cap", "plastic bottle cap", "metal bottle cap", "jar lid" | Reward |
| Things to reject | "piece of paper", "lighter", "twig", "food", "stone", "dirt crumbs", "leaf", "empty tray" | Compete with the cap descriptions |

Each description is used as "a photo of a …". A photo is YES when its `cap_score` reaches **0.6** (owner's choice).

**How the descriptions compete:** the model shares 100 % among all descriptions, and only the cap group counts toward YES. Every other description is a competitor, not an extra way to pass. Descriptions are therefore listed only for things the box must reject (they give a stone, a leaf or an empty tray somewhere to go). Look-alikes that may be rewarded, such as coins, buttons and washers, are deliberately not listed: as competitors, "button" took most of the vote from caps seen from above (a white cap 0.04 with it, 0.99 without).

- **Weights:** `timm/MobileCLIP2-S0-OpenCLIP`, revision `095906d28bf54d7584dc411e8ffe448f34289e05`, `open_clip_model.safetensors`, SHA-256 `ab91a1a0c4330d6b1913e24d5035dfdea15423316aaec649610c6b1c6ddd0e95`. Licensed under Apple's research licence (`apple-amlr`), which restricts their use; they are not part of this repository.
- **Export:** `deploy/build_model.sh` downloads the weights and runs `export_model.py`, which writes one ONNX file (`model.onnx`, 46 MB) with the image encoder and the description embeddings built in, plus the description list in its metadata. On the Pi only onnxruntime is needed: the model is ready about 1.5 s after start, instead of about 90 s with PyTorch. The detector refuses a model file whose description list differs from `recognition.py`.
- **Preprocessing (essential):** the analysed area is padded to a square with white, resized bilinearly to 256 × 256, values 0–1, **no mean/std normalisation**. Loaded from a local file, open_clip silently uses OpenAI CLIP's normalisation instead, which ruins the scores; `export_model.py` and `recognition.py` therefore set the preprocessing explicitly.
- **Speed on the Pi 3:** with the detector stopped, 0.76 s per analysis on 4 threads, 0.89 s on 3, 1.22 s on 2, 2.20 s on 1. In real visits (camera and light working at the same time) 4 threads took about 2 s because the supply sagged and the Pi slowed its CPU; production uses 3 threads: about 0.95 s (2026-10-17).

## Bench session, 2026-10-15

91 rounds of three photos in the bench intake (a round wooden floor seen down a round tube), no servo movement, sorted by eye: 32 drink caps (crown caps and plastic caps, top up and upside down), 12 larger lids (jar and container lids, about 45–70 mm), 37 empty trays.

| Description set | Caps ≥ 0.7 | Larger lids ≥ 0.7 | Empty trays ≥ 0.7 |
|---|---|---|---|
| Caps, as above | 93% (median 0.96) | 50% | 33% |
| Caps + "jar lid" as a cap description | 94% | 69% | 96% |
| "jar lid" among the other descriptions | 46% | — | — |

- Caps are recognised well. "Jar lid" among the other descriptions took half of the real caps, so it is not used there.
- **The empty tray was the problem:** seen from above, the round floor inside the round tube looks like a cap or a lid. Hence a square or rectangular plain grey tray ([MECHANICS](MECHANICS.md)) and a fixed tray area per unit ([ALGORITHM](ALGORITHM.md)).
- The model cannot tell a drink cap from a larger lid; the intake slot limits the size instead.

## Grey-card session, 2026-10-15 (dim light: worst case)

A plain grey card as the tray floor; the light at its limit (60 ms, highest gain, average brightness 51 of 255, warm room light leaking in). 21 rounds of three photos: 8 caps, 9 lids, 4 other objects (feather, paper, a plastic stick, a plastic piece), plus two photos of the empty card. Best score per round with the four cap descriptions:

| Group | Scores |
|---|---|
| Empty card | 0.001 |
| Other objects | at most 0.057 |
| Caps | 1.00 · 0.22 · 0.49 · 0.99 · 0.09 · 0.95 · 0.71 · 0.94 |
| Lids | 1.00 · 0.98 · 0.81 · 0.85 · 0.56 · 0.56 · 0.03 · 0.04 · 0.05 |

- **The grey card solved the empty-tray problem:** 0.001 instead of up to 0.99 on the round floor.
- **"Jar lid" now joins the cap descriptions** (owner's decision): on the grey card it raises lids without raising anything else.
- Scores are stable within a round; dim light lowers some objects consistently. The white cap scored 0.09, and the same crown cap 0.22 here against 0.87 in the brighter tube.
- The square container lid (about 8 cm, 0.03–0.05) would be turned away by the intake slot anyway.

## Second grey-card session, 2026-10-15 (leaks sealed, reflectors; still dim)

Light leaks sealed and white reflectors added: colours became neutral, brightness stayed about 52 of 255 (the light is still far from the card). 16 rounds: empty card, crown caps, white and blue caps, stone, leaf, twig, a small plant, a coin, the large container lid, paper.

Both grey-card sessions together (14 caps, 6 lids, 10 other objects, the empty card), best score per round:

| | With coin, button, washer listed | **Without them (current)** |
|---|---|---|
| Caps ≥ 0.6 | 9 of 14 | **14 of 14** (lowest 0.98) |
| Lids ≥ 0.6 | 4 of 6 | **6 of 6** (lowest 0.81) |
| Other objects | at most 0.06 | at most 0.11 |
| Empty card | 0.00 | 0.00 |
| Coin | 0.22 | 0.99 (rewarded; accepted by the owner) |
| Large container lid (about 8 cm) | 0.01–0.05 | 0.01–0.05 (too large for the slot anyway) |

Owner's decisions: coin, button and washer removed from the descriptions; threshold **0.6**. The sample is still small; the live test with the finished box will show more. Brighter light remains planned ([LIGHTING](LIGHTING.md)).

## Review of all kept visits, 2026-10-17 (known limit, accepted)

All 126 visits then kept on the Pi were checked by eye. 113 decisions were right: 84 caps and lids accepted (all that were in view), 29 other items rejected. 9 non-caps were accepted, all round or dome-shaped seen from above: a plug-in night light (twice, 0.92 and 0.95), a metal tea-infuser ball (three times, 0.73–0.82), a roll of tape (0.98), a small red plastic cup (0.94), a capacitor standing on its end (0.92) and a cork disc (0.64). Two caps were missed because they lay almost outside the camera view. A coin was accepted, as allowed (coins need not be rejected).

The scores of these items (0.64–0.98) overlap those of real caps (lowest 0.63, 0.63, 0.75, 0.78), so no threshold separates them. The owner decided not to add further checks or training for this: the zero-shot model accepts some round non-cap objects, and that is acceptable for now. A model trained on the box's own photos remains the option if it ever matters ([ROADMAP](ROADMAP.md)).
