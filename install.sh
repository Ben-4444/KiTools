#!/bin/bash

chmod +x KiTools.py
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
sudo ln -s "$SCRIPT_DIR/KiTools.py" /usr/bin/KiTools