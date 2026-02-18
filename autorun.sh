#!/usr/bin/env bash
# autorun.sh
#
# Goal:
#   Installs and configures XAMPP with packaged installer 
#
# Apache Friends documented install steps on Linux:
#   chmod 755 xampp-linux-*-installer.run
#   sudo ./xampp-linux-*-installer.run
# and it installs under /opt/lampp. [web:32]

set -euo pipefail

############################################
# Find the directory this script lives in
############################################
# This is important because autostart scripts often run with a different working directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # robust “script’s own folder” pattern [web:108]

############################################
# CONFIG: Installer filename pattern
############################################
# If you want to force an exact filename, replace the glob with a specific name.
INSTALLER_GLOB="xampp-linux-*-installer.run"

############################################
# CONFIG: Where XAMPP is expected to be installed
############################################
XAMPP_DIR="/opt/lampp"      # XAMPP installs below /opt/lampp per Apache Friends FAQ [web:32]
XAMPP_CTL="$XAMPP_DIR/lampp"

echo "[INFO] Script directory: $SCRIPT_DIR"

############################################
# Step A: If XAMPP already installed, stop here
############################################
if [[ -x "$XAMPP_CTL" ]]; then
  echo "[INFO] XAMPP already installed at $XAMPP_CTL; nothing to do."
  exit 0
fi

############################################
# Step B: Locate installer in same folder
############################################
# We search only in SCRIPT_DIR, so the ZIP bundle is self-contained.
shopt -s nullglob
installers=("$SCRIPT_DIR"/$INSTALLER_GLOB)
shopt -u nullglob

if [[ "${#installers[@]}" -eq 0 ]]; then
  echo "[ERROR] No installer found in $SCRIPT_DIR matching: $INSTALLER_GLOB"
  echo "        Put the XAMPP .run file in the same folder as this script."
  exit 1
fi

if [[ "${#installers[@]}" -gt 1 ]]; then
  echo "[ERROR] Found multiple installers. Keep only one in the folder:"
  printf '        %s\n' "${installers[@]}"
  exit 1
fi

INSTALLER="${installers[0]}"
echo "[INFO] Found installer: $INSTALLER"

############################################
# Step C: Make installer executable + run it
############################################
# These are exactly the steps in the Apache Friends FAQ. [web:32]
chmod 755 "$INSTALLER"        # [web:32]
sudo "$INSTALLER"             # [web:32]

############################################
# Step D: Verify install location exists
############################################
if [[ ! -x "$XAMPP_CTL" ]]; then
  echo "[ERROR] Installer finished, but $XAMPP_CTL not found/executable."
  echo "        Check installer output for errors."
  exit 1
fi

echo "[INFO] XAMPP installed successfully under $XAMPP_DIR. [web:32]"
echo "[INFO] You can start it with: sudo /opt/lampp/lampp start  (documented) [web:32]"
