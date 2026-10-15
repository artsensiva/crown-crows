"""Setup step (setup computer or the Pi, offline): export MobileCLIP2-S0 with the label embeddings to one ONNX file."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from recognition import LABELS, METADATA_KEY


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True, help="open_clip_model.safetensors")
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    if options.output.exists():
        parser.error("Output already exists; choose a new file")
    if hashlib.sha256(options.weights.read_bytes()).hexdigest() != options.sha256:
        parser.error("Weights checksum mismatch")
    os.environ["HF_HUB_OFFLINE"] = "1"
    import onnx
    import open_clip
    import torch
    from timm.utils import reparameterize_model

    model = open_clip.create_model("MobileCLIP2-S0", pretrained=str(options.weights))
    model = reparameterize_model(model.eval())
    tokenizer = open_clip.get_tokenizer("MobileCLIP2-S0")
    with torch.no_grad():
        text = model.encode_text(tokenizer([f"a photo of a {label}" for label in LABELS]))
        text /= text.norm(dim=-1, keepdim=True)

    class Recogniser(torch.nn.Module):
        # Input: 1x3x256x256 RGB in [0, 1], no mean/std normalization.
        def __init__(self):
            super().__init__()
            self.visual = model.visual
            self.register_buffer("text", text)

        def forward(self, image):
            features = self.visual(image)
            features = features / features.norm(dim=-1, keepdim=True)
            return (100 * features @ self.text.T).softmax(dim=-1)

    options.output.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(Recogniser().eval(), torch.rand(1, 3, 256, 256), str(options.output), input_names=["image"],
                      output_names=["probabilities"], opset_version=17, dynamo=False)
    exported = onnx.load(str(options.output))
    exported.metadata_props.add(key=METADATA_KEY, value=json.dumps(LABELS))
    exported.metadata_props.add(key="crown_crows_source_sha256", value=options.sha256)
    onnx.save(exported, str(options.output))
    print(json.dumps({"output": str(options.output), "sha256": hashlib.sha256(options.output.read_bytes()).hexdigest(),
                      "labels": LABELS}))


if __name__ == "__main__":
    main()
