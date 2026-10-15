"""Zero-shot recognition of bottle caps and lids with MobileCLIP2-S0."""
import json

# Zero-shot labels. The first three count as a cap (their probabilities are
# summed into "cap_score"); the rest compete with them. Chosen on the
# 2026-10-15 bench session (docs/RECOGNITION.md). Changing this list changes
# every score and requires re-exporting the model (deploy/build_model.sh).
CAP_LABELS = ["bottle cap", "plastic bottle cap", "metal bottle cap"]
OTHER_LABELS = ["piece of paper", "lighter", "twig", "food", "stone", "dirt crumbs", "coin", "button",
                "metal washer", "leaf", "empty tray"]
LABELS = CAP_LABELS + OTHER_LABELS
METADATA_KEY = "crown_crows_labels"


def pad_square(rgb):
    from PIL import Image

    image = Image.fromarray(rgb)
    side = max(image.size)
    square = Image.new("RGB", (side, side), (255, 255, 255))
    square.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
    return square


def result(probabilities):
    scores = {label: round(float(value), 4) for label, value in zip(LABELS, probabilities)}
    return {"cap_score": round(sum(scores[label] for label in CAP_LABELS), 4), "scores": scores}


def load_model(path, threads):
    # The exported model.onnx holds the image encoder and the label
    # embeddings, so neither torch nor open_clip is needed on the Pi and the
    # model is ready about 1.5 s after start.
    import numpy
    import onnxruntime
    from PIL import Image

    settings = onnxruntime.SessionOptions()
    settings.intra_op_num_threads = threads
    settings.inter_op_num_threads = 1
    session = onnxruntime.InferenceSession(str(path), settings, providers=["CPUExecutionProvider"])
    labels = json.loads(session.get_modelmeta().custom_metadata_map.get(METADATA_KEY, "null"))
    if labels != LABELS:
        raise RuntimeError("Labels in the model file differ from LABELS in recognition.py; re-export the model")

    def score(rgb):
        # Same as open_clip's MobileCLIP2 preprocessing on a square image:
        # bilinear resize to 256, values in [0, 1], no mean/std normalization.
        # (Local weights make open_clip fall back silently to OpenAI CLIP
        # normalization, which ruins the scores.)
        square = pad_square(rgb).resize((256, 256), Image.Resampling.BILINEAR)
        tensor = (numpy.asarray(square, dtype=numpy.float32) / 255).transpose(2, 0, 1)[None]
        return result(session.run(None, {"image": tensor})[0][0])

    return score
