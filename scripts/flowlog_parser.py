"""
flowlog_parser.py
-----------------
Parses AWS VPC Flow Log files and summarizes rejected traffic
by source IP and destination port.

AWS VPC Flow Log format (version 2, space-delimited):
  version account-id interface-id srcaddr dstaddr srcport dstport
  protocol packets bytes start end action log-status

Usage:
    python flowlog_parser.py <path-to-flow-log-file>

Example:
    python flowlog_parser.py flowlog.txt
"""

import sys
from collections import defaultdict


def parse(filepath):
    rejected = defaultdict(int)
    accepted = defaultdict(int)
    total = 0
    bad = 0

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("version"):
                continue
            parts = line.split()
            if len(parts) < 14:
                bad += 1
                continue
            total += 1
            src = parts[3]
            dst_port = parts[6]
            action = parts[12]
            key = f"{src:<18} -> port {dst_port}"
            if action == "REJECT":
                rejected[key] += 1
            else:
                accepted[key] += 1

    return rejected, accepted, total, bad


def report(rejected, accepted, total, bad):
    total_rejects = sum(rejected.values())
    total_accepts = sum(accepted.values())

    print("\n╔══════════════════════════════════════════╗")
    print("║       VPC Flow Log — Traffic Summary     ║")
    print("╚══════════════════════════════════════════╝\n")
    print(f"  Records parsed    : {total}")
    print(f"  Malformed skipped : {bad}")
    print(f"  ACCEPT events     : {total_accepts}")
    print(f"  REJECT events     : {total_rejects}")

    if not rejected:
        print("\n  No rejected connections found in this log.\n")
        return

    print("\n  ── Top 10 Rejected Source → Port ──\n")
    top = sorted(rejected.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (key, count) in enumerate(top, 1):
        bar = "█" * min(count, 40)
        print(f"  {i:>2}. {count:>5}x  {key}")
        print(f"       {bar}")

    print("\n  ── Most Targeted Ports ──\n")
    by_port = defaultdict(int)
    for key, count in rejected.items():
        port = key.split("port ")[-1].strip()
        by_port[port] += count
    for port, count in sorted(by_port.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  port {port:<8} : {count} rejections")

    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    try:
        rejected, accepted, total, bad = parse(sys.argv[1])
        report(rejected, accepted, total, bad)
    except FileNotFoundError:
        print(f"File not found: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
