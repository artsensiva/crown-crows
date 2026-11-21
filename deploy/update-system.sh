#!/usr/bin/env bash
# Monthly system update for the box (run with sudo, when the box is idle and the supply is quiet).
# Since 2026-11-21 the automatic package timers are off (deploy/trim-system.sh), so without this the
# Pi never gets security fixes. The camera stack is held back: it is what the recognition and the
# exposure control were tested with, and an automatic change of it could break the box silently.
# After the update: run selftest.py (the detector must be stopped), look at the dashboard, and reboot
# if the script says so.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Run with sudo: sudo bash $0" >&2
    exit 1
fi

HOLD="rpicam-apps-lite rpicam-apps-core librpicam-app1 libcamera0.7 libcamera-ipa libcamera-tools python3-libcamera"
for package in $HOLD; do
    if dpkg -s "$package" >/dev/null 2>&1; then apt-mark hold "$package" >/dev/null; fi
done
echo "Held back (camera stack): $(apt-mark showhold | paste -sd' ')"

apt-get update
echo "--- What would be upgraded:"
apt-get -s upgrade | grep '^Inst' | cut -d' ' -f2 | paste -sd' '
read -r -p "Upgrade now? [y/N] " answer
if [ "$answer" = "y" ]; then
    apt-get -y upgrade
    apt-get -y autoremove
    echo "Done on $(date +%F)."
    if [ -f /var/run/reboot-required ]; then echo "A reboot is needed (kernel or core libraries)."; fi
fi
