import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Print the detector's visits: decision, scores, timing, servo stroke")
    parser.add_argument("--log", type=Path, default=Path.home() / "crown-crows/logs/detect.jsonl")
    parser.add_argument("--all-boots", action="store_true", help="Include visits from earlier boots")
    parser.add_argument("--last", type=int, default=0, help="Only the last N visits")
    options = parser.parse_args()
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()[:8]
    rows = [json.loads(line) for line in options.log.open() if line.strip()]
    rows = [row for row in rows if options.all_boots or row.get("boot") == boot]
    if options.last:
        rows = rows[-options.last:]
    print(f"{len(rows)} visit(s){'' if options.all_boots else ' since this boot'} ({options.log})")
    print(f"{'#':>3} {'decision':8} {'photos':6} {'best':6} {'at photo':8} {'seconds':7} {'servo':24} batch")
    for row in rows:
        photos = row.get("photos") or []
        best = max(photos, key=lambda photo: photo["cap_score"], default=None)
        decision = row.get("decision")
        servo = row.get("servo") or {}
        stroke = f"{servo.get('stroke', '-')} {servo.get('outcome', '')}".strip() if servo else "off"
        print(f"{row.get('sequence', '?'):>3} {str(decision):8} {row.get('photos_taken', '-')!s:6} "
              f"{(best['cap_score'] if best else 0):<6.3f} "
              f"{(best['photo'] if best else '-')!s:8} {row.get('trigger_to_decision_seconds', 0) or 0:<7.2f} "
              f"{stroke:24} {row.get('batch', '')}")


if __name__ == "__main__":
    main()
