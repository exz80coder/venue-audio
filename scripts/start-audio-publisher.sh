#!/bin/bash

ffmpeg \
-f alsa \
-ar 48000 \
-ac 2 \
-i plughw:0,0 \
-vn \
-c:a libopus \
-b:a 64k \
-f rtsp \
-rtsp_transport tcp \
rtsp://127.0.0.1:8554/venueaudio
