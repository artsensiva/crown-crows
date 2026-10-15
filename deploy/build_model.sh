#!/bin/bash
# Builds the recognition model models/mobileclip2-s0/model.onnx (46 MB) on a
# setup computer (Linux or macOS, Python 3.10+, about 2 GB free, internet).
# The weights are not part of the repository: they are downloaded at a pinned
# revision and checked by SHA-256. They are licensed under Apple's research
# licence (apple-amlr); review it before use.
#
#   cd crown-crows && bash deploy/build_model.sh
#
# Then copy models/mobileclip2-s0/model.onnx to the Pi (docs/DEPLOY.md).
# VENV=<path> reuses an existing environment that already has the packages.
set -euo pipefail
cd "$(dirname "$0")/.."
REVISION=095906d28bf54d7584dc411e8ffe448f34289e05
WEIGHTS_SHA256=ab91a1a0c4330d6b1913e24d5035dfdea15423316aaec649610c6b1c6ddd0e95
WEIGHTS=models/mobileclip2-s0/open_clip_model.safetensors
OUTPUT=models/mobileclip2-s0/model.onnx
VENV=${VENV:-.venv-export}

mkdir -p models/mobileclip2-s0
if ! echo "$WEIGHTS_SHA256  $WEIGHTS" | sha256sum -c --quiet 2>/dev/null; then
    echo "Downloading MobileCLIP2-S0 weights (300 MB, revision $REVISION)"
    curl -L --fail -o "$WEIGHTS" \
        "https://huggingface.co/timm/MobileCLIP2-S0-OpenCLIP/resolve/$REVISION/open_clip_model.safetensors"
    echo "$WEIGHTS_SHA256  $WEIGHTS" | sha256sum -c --quiet
fi
echo "weights checksum OK"

if [ ! -x "$VENV/bin/python" ]; then
    echo "Creating $VENV with CPU-only PyTorch and open_clip (only needed for this export)"
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet torch --index-url https://download.pytorch.org/whl/cpu
    "$VENV/bin/pip" install --quiet open_clip_torch==3.3.0 timm==1.0.30 onnx onnxscript
fi

if [ -f "$OUTPUT" ]; then
    echo "$OUTPUT already exists; delete it to rebuild"
else
    "$VENV/bin/python" -B export_model.py --weights "$WEIGHTS" --sha256 "$WEIGHTS_SHA256" --output "$OUTPUT"
fi
sha256sum "$OUTPUT"
echo "If the checksum differs from 1ac057e7...24f8 (another PyTorch version), the scores are still identical:"
echo "pass the new checksum to the service with --model-sha256 (deploy/crown-crows-detect.service) and to install.sh."
