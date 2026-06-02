#!/bin/bash

echo "Testing audio capture from StarTech Line In..."

arecord -D plughw:0,0 -r 48000 -c 2 -f S16_LE -d 5 test.wav

echo "Recording complete:"
ls -lh test.wav

echo "Playing back..."
pw-play test.wav
