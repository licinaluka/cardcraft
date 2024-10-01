#!/bin/bash

pkill -TERM -P $(cat .pid) && kill -TERM $(cat .pid)
