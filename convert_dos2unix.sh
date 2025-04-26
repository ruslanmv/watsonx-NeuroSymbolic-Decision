#!/usr/bin/env bash
# convert_dos2unix.sh
#
# Convert all *.env and *.sh files to Unix LF endings.
# Usage:
#   ./convert_dos2unix.sh            # scan the current directory
#   ./convert_dos2unix.sh /path/dir  # scan /path/dir recursively
#
set -euo pipefail
shopt -s nullglob

# ── prerequisites ────────────────────────────────────────────────────────────
if ! command -v dos2unix >/dev/null 2>&1; then
  echo "Error: dos2unix is not installed. Install it first (e.g. sudo apt install dos2unix)." >&2
  exit 1
fi

# ── directory to process (default '.') ───────────────────────────────────────
TARGET_DIR="${1:-.}"

# ── conversion loop ─────────────────────────────────────────────────────────
find "$TARGET_DIR" -type f \( -name "*.env" -o -name "*.sh" \) -print0 |
while IFS= read -r -d '' file; do
  echo "Converting $file"
  dos2unix "$file"
done

echo "✔ All matching files converted."
echo "✔ Done."