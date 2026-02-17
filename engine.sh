#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/.venv/bin/activate

LOGfile="$DIR/engine_debug.log"

echo "--- Starting Engine at $(date) ---" >> "$LOGfile"

python3 -u "$DIR/main.py"