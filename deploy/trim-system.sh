#!/usr/bin/env bash
# Switches off what a headless Crown Crows box does not use (run once with sudo; safe to repeat):
#   - Bluetooth (service and radio): no use, and its start-up timeouts fill the journal;
#   - the package-manager timers (apt-daily, apt-daily-upgrade, man-db, dpkg-db-backup): they start
#     work at random times, possibly during a visit; updates are done by hand (deploy/update_pi.sh);
#   - udisks2 (automounting of drives).
# Not touched: cloud-init (it may patch the Wi-Fi settings at boot) and avahi (the name raspberrypi.local).
# Undo: sudo systemctl enable --now <unit> for each unit below, and restore /boot/firmware/config.txt.bak-trim.
# The Bluetooth radio is switched off at the next reboot.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Run with sudo: sudo bash $0" >&2
    exit 1
fi

for unit in bluetooth.service apt-daily.timer apt-daily-upgrade.timer man-db.timer dpkg-db-backup.timer udisks2.service; do
    if systemctl list-unit-files "$unit" --no-legend | grep -q .; then
        systemctl disable --now "$unit" 2>&1 | tail -1 || true
        echo "off: $unit"
    fi
done

config=/boot/firmware/config.txt
if ! grep -q '^dtoverlay=disable-bt' "$config"; then
    cp -n "$config" "$config.bak-trim"
    # the last section of the file is [all], so the line applies to every board
    printf '\ndtoverlay=disable-bt\n' >> "$config"
    echo "Bluetooth radio off after the next reboot (backup: $config.bak-trim)"
else
    echo "Bluetooth radio already off in $config"
fi
echo "Done. State:"
systemctl is-enabled bluetooth.service apt-daily.timer apt-daily-upgrade.timer man-db.timer dpkg-db-backup.timer udisks2.service 2>&1 | paste -sd' '
