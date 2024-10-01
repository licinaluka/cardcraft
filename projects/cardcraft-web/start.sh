#!/bin/bash

if pgrep -F .pid; then
    echo Already up
    exit
fi
                                                     
export LOCALONLY=true
poetry run nohup python3 main.py 2>&1 &
echo $! > .pid
