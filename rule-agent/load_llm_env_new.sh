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
# When a script is sourced, ${BASH_SOURCE[0]} is the path to the script itself,
# and ${0} is the name of the shell (e.g., -bash).
# When executed, both are the path to the script.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: This script must be sourced, not executed." >&2
  echo "Run it with:   source $(basename "${BASH_SOURCE[0]}")" >&2
  # exit 1 - Cannot exit the parent shell, use return instead if sourced
  # If executed, exit is appropriate.
  exit 1
fi

# Abort sourcing if any command fails
# Note: This affects the *caller's* shell until 'return' or 'set +e'
set -e

# ──────────────────────────────────────────────────────────────────────────────
# 1. Activate Python virtual-environment
# ──────────────────────────────────────────────────────────────────────────────
VENV_DIR=".venv"
VENV_ACTIVATE="${VENV_DIR}/bin/activate"

echo "🐍 Checking for virtual environment..."
if [ ! -f "$VENV_ACTIVATE" ]; then
  echo "ERROR: Virtual environment activation script not found at '$VENV_ACTIVATE'" >&2
  echo "Please create the virtual environment (e.g., 'python3 -m venv ${VENV_DIR}')" >&2
  # Stop sourcing the script if venv is missing
  set +e # Turn off exit on error before returning
  return 1
fi

echo "🔐 Activating virtual environment: ${VENV_ACTIVATE}"
# shellcheck disable=SC1090
source "$VENV_ACTIVATE"

# ──────────────────────────────────────────────────────────────────────────────
# 2. Core backend variables
# ──────────────────────────────────────────────────────────────────────────────
echo "🔧 Setting core backend variables..."
export ODM_SERVER_URL="http://localhost:9060"
export ODM_USERNAME="odmAdmin"
export ODM_PASSWORD="odmAdmin"
export PYTHONUNBUFFERED="1"

# Define DATADIR relative to the script's location for robustness
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
export DATADIR="${SCRIPT_DIR}/../data"
echo "   - DATADIR set to: ${DATADIR}"


# ──────────────────────────────────────────────────────────────────────────────
# 3. Load additional vars from ../llm.env relative to the script
# ──────────────────────────────────────────────────────────────────────────────
ENV_FILE="${SCRIPT_DIR}/../llm.env"
echo "📄 Loading variables from '${ENV_FILE}'..."

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: Environment file '${ENV_FILE}' not found." >&2
  set +e # Turn off exit on error before returning
  return 1
fi

# Use 'set -a' to automatically export variables read by 'source' or '.'
# This avoids the need for the complex while loop and eval
# However, it requires the .env file to be strictly in 'export KEY=VALUE' or 'KEY=VALUE' format.
# Let's stick to the original loop method for compatibility with the provided .env format,
# but ensure robust parsing.

# Backup IFS and set it to newline only to handle values with spaces correctly
OLD_IFS="$IFS"
IFS=$'\n'

while IFS= read -r line || [[ -n $line ]]; do
  # Trim leading/trailing whitespace from the line itself
  line="$(echo "$line" | xargs)"

  # Skip comments and blank lines
  [[ "$line" =~ ^# ]] && continue
  [[ -z "$line" ]] && continue

  # Ensure there is an '=' sign
  if [[ "$line" != *'='* ]]; then
     echo "   - Skipping malformed line (no '='): $line" >&2
     continue
  fi

  # Extract key and value
  key="${line%%=*}"
  value="${line#*=}"

  # Trim whitespace from key and value
  key="$(echo "$key" | xargs)"
  # Value trimming can be tricky if spaces are intended. The original script didn't trim value.
  # Let's keep the original behavior for value.

  # Skip if key is empty after trimming
  [[ -z "$key" ]] && continue

  # Use printf %q for safe quoting, then eval to export
  printf -v val_quoted '%q' "$value"
  # echo "   - Exporting: ${key}=${val_quoted}" # Uncomment for debugging
  eval "export ${key}=${val_quoted}"

done < "$ENV_FILE"

# Restore IFS
IFS="$OLD_IFS"


echo "✅ Finished setting environment variables."

# Turn off exit-on-error before returning control to the user's shell
set +e
return 0 # Indicates successful sourcing
