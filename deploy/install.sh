#!/bin/bash
# Installs the Crown Crows engine on a Raspberry Pi 3 (Raspberry Pi OS Lite 64-bit,
# Debian 13). Run on the Pi, from the crown-crows folder, while it still has a
# network connection (package downloads); afterwards it runs offline.
#
#   cd ~/crown-crows && bash deploy/install.sh
#
# Safe to run again: every step checks what is already done, and sudo (the
# password) is only needed for steps that still have something to do.
# See docs/DEPLOY.md.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
MODEL=models/mobileclip2-s0/model.onnx
MODEL_SHA256=1ac057e79ad7c3a4ad2fe99e2555b7e0ef63cc11e6992c45e4fb235eaa2224f8
CONFIG=/boot/firmware/config.txt
REBOOT=no

step() { printf '\n== %s\n' "$1"; }

step "1/8 Checking the project files in $ROOT"
for file in detect.py servo_bench.py recognition.py selftest.py report.py lights.py \
            deploy/crown-crows-detect.service deploy/requirements-runtime.txt "$MODEL"; do
    [ -f "$file" ] || { echo "Missing $file: copy the project first (docs/DEPLOY.md)"; exit 1; }
done
echo "$MODEL_SHA256  $MODEL" | sha256sum -c --quiet && echo "model checksum OK"

step "2/8 System packages (camera tools, GPIO libraries, Python venv)"
PACKAGES="rpicam-apps-lite python3-venv python3-gpiozero python3-lgpio"
if dpkg-query -W -f='${Status}\n' $PACKAGES 2>/dev/null | grep -vq "install ok installed" \
   || [ "$(dpkg-query -W -f='${Status}\n' $PACKAGES 2>/dev/null | wc -l)" -ne 4 ]; then
    sudo apt-get update
    sudo apt-get install -y $PACKAGES
else
    echo "already installed: $PACKAGES"
fi

step "3/8 Python environment .venv-detector (runtime packages only)"
[ -x .venv-detector/bin/python ] || python3 -m venv --system-site-packages .venv-detector
# --no-warn-conflicts: the venv sees the system's Python packages, and pip
# would otherwise report unrelated conflicts among those (e.g. types-seaborn).
.venv-detector/bin/pip install --quiet --no-warn-conflicts -r deploy/requirements-runtime.txt
.venv-detector/bin/python -c "import onnxruntime, cv2, numpy, PIL, gpiozero, lgpio; print('imports OK: onnxruntime', onnxruntime.__version__, 'cv2', cv2.__version__)"

step "4/8 Hardware PWM for the servo on GPIO18"
if grep -q '^dtoverlay=pwm,pin=18,func=2' "$CONFIG"; then
    echo "already in $CONFIG"
else
    echo 'dtoverlay=pwm,pin=18,func=2' | sudo tee -a "$CONFIG" >/dev/null
    echo "added to $CONFIG (takes effect after a reboot)"
    REBOOT=yes
fi

step "5/8 Permissions: $USER in the gpio and video groups"
if id -nG "$USER" | grep -qw gpio && id -nG "$USER" | grep -qw video; then
    echo "already in gpio and video"
else
    sudo usermod -aG gpio,video "$USER"
fi

step "6/8 Keep the system log across reboots (capped at 50 MB)"
# Raspberry Pi OS keeps the log in RAM by default (40-rpi-volatile-storage.conf);
# without a persistent log a crash leaves no evidence.
if [ -d /var/log/journal ] && grep -qs '^Storage=persistent' /etc/systemd/journald.conf.d/*.conf; then
    echo "already persistent"
else
    sudo mkdir -p /etc/systemd/journald.conf.d /var/log/journal
    printf '[Journal]\nStorage=persistent\nSystemMaxUse=50M\n' | sudo tee /etc/systemd/journald.conf.d/90-crown-crows.conf >/dev/null
    sudo systemctl restart systemd-journald
    # Move the log from RAM to the card now; otherwise this happens only at the next boot.
    sudo journalctl --flush
fi

step "7/8 Service crown-crows-detect: start at boot without a login"
if [ "$(loginctl show-user "$USER" -p Linger --value 2>/dev/null)" = yes ]; then
    echo "lingering already enabled"
else
    sudo loginctl enable-linger "$USER"
fi
mkdir -p "$HOME/.config/systemd/user" logs captures config
cp deploy/crown-crows-detect.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable crown-crows-detect

step "8/8 Checks and self-test"
rpicam-hello --list-cameras 2>&1 | grep -E "imx|No cameras" || echo "camera list not available"
if [ -f config/local.servo.json ]; then
    echo "servo calibration present: $(tr -d '\n ' < config/local.servo.json | cut -c1-80)"
else
    echo "NO servo calibration yet: the service detects without strokes (red blip every 5 s) until you calibrate (docs/SERVO.md)"
fi
# The self-test runs the production logic with this Pi's camera on the
# tray photos shipped in selftest-photos/, with the network blocked.
# It does not move the servo.
systemctl --user stop crown-crows-detect 2>/dev/null || true
selftest_output=$(.venv-detector/bin/python -B selftest.py 2>&1) || true
if grep -q "^RESULT" <<< "$selftest_output"; then
    grep -E "^(scenario|crown|plastic|light|empty|piece|feather|network|RESULT)" <<< "$selftest_output"
else
    echo "Self-test could not run (camera not connected, or enabled only after the reboot?); last lines:"
    tail -n 3 <<< "$selftest_output"
    echo "Repeat it later: systemctl --user stop crown-crows-detect && .venv-detector/bin/python -B selftest.py && systemctl --user start crown-crows-detect"
fi

if [ "$REBOOT" = yes ]; then
    printf '\nDone. Reboot now (sudo reboot) to activate hardware PWM; the service starts by itself.\n'
else
    systemctl --user restart crown-crows-detect
    printf '\nDone. The service is running: blue while starting, three green flashes when ready (about 2 minutes).\n'
fi
