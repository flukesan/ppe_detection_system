#!/bin/bash
# Launcher script for PPE Detection System on Ubuntu
# Fixes Qt/Wayland display issues

# Force Qt to use X11 instead of Wayland
export QT_QPA_PLATFORM=xcb

# Suppress FFmpeg H.264 decoding warnings
export OPENCV_FFMPEG_LOGLEVEL=quiet

# Run the application
python3 main.py "$@"
