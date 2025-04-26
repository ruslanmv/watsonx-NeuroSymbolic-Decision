#!/bin/bash
set -euo pipefail

echo "🔄  Updating apt cache…"
sudo apt-get update

echo "🐍  Installing Python 3.10 support & tools…"
sudo apt-get install -y \
  python3 \
  python3-apt \
  python3-venv \
  python3-distutils \
  python3-pip \
  curl \
  gnupg \
  lsb-release \
  software-properties-common

echo "✅  Python check:"
printf "   • python3 → %s\n" "$(python3 --version)"
printf "   • pip3    → %s\n" "$(pip3 --version)"

# ────────────────────────────────────────────────────────────────────────────
# Clean up any old Node.js/libnode packages that conflict
# ────────────────────────────────────────────────────────────────────────────
echo "🧹  Removing old Node.js packages (nodejs, nodejs-doc, libnode72)…"
sudo apt-get remove -y nodejs nodejs-doc libnode72 || true
sudo apt-get autoremove -y

# ────────────────────────────────────────────────────────────────────────────
# Node.js installation from NodeSource
# ────────────────────────────────────────────────────────────────────────────
echo "🔧  Setting up NodeSource for Node.js 20.x…"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

echo "📦  Installing Node.js (with npm & npx)…"
sudo apt-get update
sudo apt-get install -y nodejs
sudo apt-get install -y default-jre

echo "✅  Node check:"
printf "   • node → %s\n" "$(node --version)"
printf "   • npm  → %s\n" "$(npm --version)"
printf "   • npx  → %s\n" "$(npx --version)"
echo "✅  Java check:"
printf "   • java → %s\n" "$(java --version)"
# ────────────────────────────────────────────────────────────────────────────
# Create & activate the Python 3.10 venv
# ────────────────────────────────────────────────────────────────────────────
if [ -d ".venv" ]; then
  echo "⚠️   .venv exists; skipping creation."
else
  echo "🐍  Creating virtual environment (.venv) with Python 3.10…"
  python3 -m venv .venv
fi

echo "🔐  Activating .venv…"
# shellcheck disable=SC1091
source .venv/bin/activate

echo "⬆️   Upgrading pip in the venv…"
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
  echo "📦  Installing Python dependencies…"
  pip install -r requirements.txt
else
  echo "📄  No requirements.txt found; skipping."
fi

echo "🎉  All set!"
echo "   • Inside .venv: $(python --version), pip $(pip --version)"
echo "   • Outside venv: python3 $(python3 --version), pip3 $(pip3 --version)"
echo "   • Node.js: node $(node --version), npm $(npm --version), npx $(npx --version)"