#!/usr/bin/env bash
#
# load_llm_env.sh – Source this file to load all backend/LLM variables
#
#   Usage:
#     source ./load_llm_env.sh
#

# ──────────────────────────────────────────────────────────────────────────────
# 0. Guard: stop early if the file is *executed* instead of *sourced*
# ──────────────────────────────────────────────────────────────────────────────
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: this script must be sourced, not executed." >&2
  echo "Run it with:   source $(basename "$0")" >&2
  exit 1
fi

# Abort on any error (still inside the caller’s shell)
set -e

# ──────────────────────────────────────────────────────────────────────────────
# 1. Activate Python virtual-environment
# ──────────────────────────────────────────────────────────────────────────────
VENV_ACTIVATE=".venv/bin/activate"      # absolute path as requested

if [ -d ".venv" ]; then

  echo "Activating virtual environment: $VENV_ACTIVATE"
  # shellcheck disable=SC1090
  source "$VENV_ACTIVATE"
else
  echo "🐍  Creating virtual environment (.venv) with Python 3.10…"
  echo "ERROR: virtual-environment not found at $VENV_ACTIVATE" >&2
  echo "Make sure the venv exists or adjust VENV_ACTIVATE in this script." >&2
fi

echo "🔐  Activating .venv…"
# shellcheck disable=SC1091
source .venv/bin/activate
echo "Setting backend environment variables …"

# ──────────────────────────────────────────────────────────────────────────────
# 2. Core backend variables
# ──────────────────────────────────────────────────────────────────────────────
echo "Setting core backend variables …"
export ODM_SERVER_URL="http://localhost:9060"
export ODM_USERNAME="odmAdmin"
export ODM_PASSWORD="odmAdmin"
export PYTHONUNBUFFERED="1"

# If you prefer the directory relative to this script, change as needed
export DATADIR="../data"

# ──────────────────────────────────────────────────────────────────────────────
# 3. Load additional vars from ../llm.env
# ──────────────────────────────────────────────────────────────────────────────
ENV_FILE="../llm.env"
echo "Loading variables from '${ENV_FILE}' …"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: environment file '${ENV_FILE}' not found." >&2
  echo "Please ensure it exists in the parent directory." >&2
  return 1
fi

while IFS= read -r line || [[ -n $line ]]; do
  [[ "$line" =~ ^\s*# ]] && continue   # skip comments
  [[ -z "$line" ]] && continue         # skip blank lines
  [[ "$line" != *'='* ]] && continue   # skip malformed lines

  key="${line%%=*}"
  value="${line#*=}"

  key="$(echo "$key" | xargs)"         # trim key
  [[ -z "$key" ]] && continue

  printf -v val_quoted '%q' "$value"
  eval "export ${key}=${val_quoted}"
done < "$ENV_FILE"

echo "Finished setting backend environment variables."

# Successful completion when sourced
return 0
