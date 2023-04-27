#!/usr/bin/env bash
ROOT_DIR=$HOME/.unscrambler_id

git clone --recursive https://github.com/winardiaris/unscrambler_id.git "$ROOT_DIR"
cd  "$ROOT_DIR"|| exit
git config --global --add safe.directory "$ROOT_DIR"