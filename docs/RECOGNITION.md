# Recognition

## Model

**MobileCLIP2-S0** (Apple), used zero-shot: no training on our photos. The model turns a picture into a list of numbers that describes what it looks like, and does the same with short text descriptions. The description closest to the picture wins. Our descriptions are in `recognition.py`:

| Group | Descriptions | Meaning |
|---|---|---|
| Caps and lids (summed into `cap_score`) | "bottle cap", "plastic bottle cap", "metal bottle cap", "jar lid" | Reward |
| Everything else | "piece of paper", "lighter", "twig", "food", "stone", "dirt crumbs", "coin", "button", "metal washer", "leaf", "empty tray" | Compete with the cap descriptions |

Each description is used as "a photo of a …". A photo is YES when its `cap_score` reaches 0.7.

- **Weights:** `timm/MobileCLIP2-S0-OpenCLIP`, revision `095906d28bf54d7584dc411e8ffe448f34289e05`, `open_clip_model.safetensors`, SHA-256 `ab91a1a0c4330d6b1913e24d5035dfdea15423316aaec649610c6b1c6ddd0e95`. Licensed under Apple's research licence (`apple-amlr`), which restricts their use; they are not part of this repository.
- **Export:** `deploy/build_model.sh` downloads the weights and runs `export_model.py`, which writes one ONNX file (`model.onnx`, 46 MB) with the image encoder and the description embeddings built in, plus the description list in its metadata. On the Pi only onnxruntime is needed: the model is ready about 1.5 s after start, instead of about 90 s with PyTorch. The detector refuses a model file whose description list differs from `recognition.py`.
- **Preprocessing (essential):** the analysed area is padded to a square with white, resized bilinearly to 256 × 256, values 0–1, **no mean/std normalisation**. Loaded from a local file, open_clip silently uses OpenAI CLIP's normalisation instead, which ruins the scores; `export_model.py` and `recognition.py` therefore set the preprocessing explicitly.
- **Speed on the Pi 3:** 0.75–1.4 s per analysis with 4 threads.

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

**Open:** the threshold. At 0.7, 4 of 8 caps; at 0.2, 7 of 8, with every other object far below. Better light comes first ([LIGHTING](LIGHTING.md)), then the threshold is set on brighter photos.
