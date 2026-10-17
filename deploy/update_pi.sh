#!/bin/bash
# Updates an installed Crown Crows Pi to the latest version from GitHub. Run on the
# setup computer, in a clone of the repository, while the Pi is on the network:
#
#   bash deploy/update_pi.sh <user>@<pi>
#
# Keeps the Pi's servo calibration, photos and logs, the model and the Python
# environment; no password needed. Extra ssh options (e.g. a key) can be given
# in SSH_OPTS. If deploy/install.sh or the model changed, run install.sh on the
# Pi afterwards (see docs/DEPLOY.md).
set -euo pipefail
cd "$(dirname "$0")/.."
TARGET=${1:?usage: bash deploy/update_pi.sh <user>@<pi>}
SSH="ssh ${SSH_OPTS:-}"

echo "== 1/4 Latest version from GitHub"
git pull --ff-only
git log --oneline -1

echo "== 2/4 Copying to $TARGET (calibration, photos, logs and model stay)"
rsync -a --exclude .git --exclude '.venv*' --exclude models --exclude captures --exclude logs --exclude config \
      -e "$SSH" ./ "$TARGET":crown-crows/

echo "== 3/4 Service file and self-test on the Pi (the service pauses for about a minute)"
# shellcheck disable=SC2029
$SSH "$TARGET" 'cd ~/crown-crows \
  && cp deploy/crown-crows-detect.service deploy/crown-crows-monitor.socket deploy/crown-crows-monitor.service ~/.config/systemd/user/ && systemctl --user daemon-reload \
  && systemctl --user stop crown-crows-detect \
  && { .venv-detector/bin/python -B selftest.py 2>/dev/null | grep -E "^(RESULT|network)" || echo "self-test did not run"; } \
  ; systemctl --user start crown-crows-detect'

echo "== 4/4 Service"
$SSH "$TARGET" 'echo "crown-crows-detect: $(systemctl --user is-active crown-crows-detect)"'
echo "Done. The light shows blue, then three green flashes when ready (about 2 minutes)."
