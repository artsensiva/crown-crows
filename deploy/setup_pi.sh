#!/bin/bash
# Installs Crown Crows on a Raspberry Pi in one command. Run on the setup
# computer, in a clone of the repository, while the Pi is on the network:
#
#   bash deploy/setup_pi.sh <user>@<pi>            # install or complete an installation
#   bash deploy/setup_pi.sh <user>@<pi> --fresh    # rebuild everything on the Pi from this version
#
# Builds the model if it is missing (deploy/build_model.sh), copies the project
# and the model to ~/crown-crows on the Pi, and runs deploy/install.sh there:
# system packages, Python environment, hardware PWM, permissions, persistent
# log, service, and the self-test. The Pi asks for its user's password only if
# a system step still has something to do.
#
# --fresh first deletes everything in ~/crown-crows on the Pi except config/
# (this unit's servo calibration and tray area), captures/ and logs/, so the
# Python environment and every file are rebuilt from this version.
# Extra ssh options (e.g. a key) can be given in SSH_OPTS.
set -euo pipefail
cd "$(dirname "$0")/.."
TARGET=${1:?usage: bash deploy/setup_pi.sh <user>@<pi> [--fresh]}
FRESH=${2:-}
SSH="ssh ${SSH_OPTS:-}"
MODEL=models/mobileclip2-s0/model.onnx

echo "== 1/4 Model"
[ -f "$MODEL" ] || bash deploy/build_model.sh
EXPECTED=$(grep -o '^MODEL_SHA256=[0-9a-f]*' deploy/install.sh | cut -d= -f2)
if ! echo "$EXPECTED  $MODEL" | sha256sum -c --quiet 2>/dev/null; then
    echo "The model's checksum differs from the one in deploy/install.sh (built with another PyTorch version?)."
    echo "Put $(sha256sum "$MODEL" | cut -c1-64) into deploy/install.sh and deploy/crown-crows-detect.service, then run this again."
    exit 1
fi
echo "model checksum OK"

echo "== 2/4 Prepare the Pi"
if [ "$FRESH" = --fresh ]; then
    # shellcheck disable=SC2029
    $SSH "$TARGET" 'systemctl --user stop crown-crows-detect 2>/dev/null || true
        if [ -d ~/crown-crows ]; then
            cd ~/crown-crows && find . -mindepth 1 -maxdepth 1 ! -name config ! -name captures ! -name logs -exec rm -rf {} +
            echo "cleared ~/crown-crows (kept: $(ls -m 2>/dev/null))"
        fi'
else
    echo "keeping what is already installed (use --fresh to rebuild everything)"
fi

echo "== 3/4 Copy the project and the model to $TARGET:crown-crows/"
rsync -a --exclude .git --exclude '.venv*' --exclude __pycache__ --exclude captures --exclude logs --exclude config \
      -e "$SSH" ./ "$TARGET":crown-crows/

echo "== 4/4 Install on the Pi"
# -t: a terminal, so the Pi can ask for the password if a system step needs it.
$SSH -t "$TARGET" 'cd ~/crown-crows && bash deploy/install.sh'
