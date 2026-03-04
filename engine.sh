#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/.venv/bin/activate

python3 -u "$DIR/src/biasfish/main.py"