#!/usr/bin/env python3
"""Skillshelf usage tracker — logs skill invocations for usage analytics.

This script is designed to be called from a Claude Code hook (PostToolUse on Skill tool)
or manually. It appends a usage event to the usage log file.

Usage:
    python3 track-usage.py <skill-name>
    python3 track-usage.py "build-mcp-server"
    python3 track-usage.py --list          # Show usage summary
    python3 track-usage.py --reset         # Clear all usage data
"""

import json
import sys
from datetime import datetime
from pathlib import Path

CACHE_DIR = Path.home() / ".claude" / "cache"
USAGE_LOG = CACHE_DIR / "skillshelf-usage.json"


def load_usage():
    if USAGE_LOG.is_file():
        try:
            with open(USAGE_LOG) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_usage(data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(USAGE_LOG, "w") as f:
        json.dump(data, f, indent=2)


def log_usage(skill_name):
    """Record a usage event for a skill."""
    data = load_usage()
    now = datetime.now().isoformat()

    if skill_name not in data:
        data[skill_name] = {"count": 0, "first_used": now, "last_used": now}

    data[skill_name]["count"] += 1
    data[skill_name]["last_used"] = now
    save_usage(data)
    print(f"Logged usage: {skill_name} (total: {data[skill_name]['count']})")


def show_list():
    """Print usage summary sorted by count."""
    data = load_usage()
    if not data:
        print("No usage data yet. Skills will be tracked as you use them.")
        return

    print(f"{'Skill':<40} {'Uses':>5}  {'Last Used':<20}")
    print("-" * 70)
    for name, info in sorted(data.items(), key=lambda x: -x[1]["count"]):
        last = info["last_used"][:10] if info["last_used"] else "never"
        print(f"{name:<40} {info['count']:>5}  {last:<20}")


def reset():
    """Clear all usage data."""
    save_usage({})
    print("Usage data cleared.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: track-usage.py <skill-name> | --list | --reset")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "--list":
        show_list()
    elif arg == "--reset":
        reset()
    else:
        log_usage(arg)
