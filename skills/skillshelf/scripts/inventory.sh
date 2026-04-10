#!/usr/bin/env bash
# skillshelf scanner — thin wrapper that calls the Python scanner
# Usage: inventory.sh [--include-github] [--refresh] [--cache-dir PATH]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/scan.py" "$@"
