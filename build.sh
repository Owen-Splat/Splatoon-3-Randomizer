#!/bin/bash
set -e
python3 -m PyInstaller --log-level=WARN randomizer.spec
python3 build.py