#!/bin/bash

/home/gfurse/venue-audio/scripts/fix-audio-input-tv2.sh
sleep 2

exec ffmpeg \
-f alsa \
-ar 48000 \
-ac 2 \
-i plughw:3,0 \
-vn \
-c:a libopus \
-b:a 64k \
-f rtsp \
-rtsp_transport tcp \
rtsp://127.0.0.1:8554/tv2
