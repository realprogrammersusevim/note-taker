#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"
source venv/bin/activate
venv/bin/python3 main.py -c config.json
