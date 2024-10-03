#!/bin/bash

set -e

touch .pid

if pgrep -F .pid; then
    echo Already up
    exit
fi
                                                     
$HOME/.local/bin/poetry run nohup python3 main.py > /tmp/cardcraft.log 2>&1 &
echo $! > .pid
